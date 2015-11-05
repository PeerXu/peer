import os
import libvirt_qemu
from flask import json
from libvirt import libvirtError

from peer.server.main import get_app
from peer.server.utils import open_libvirt_connection
from peer.server.common.agent import PeerAgent
from peer.server.config import get_config
from peer.server.common import task

CONFIG = get_config()

KVM_INSTANCE_TEMPLATE = '''
<domain type='kvm'>
  <name>{name}</name>
  <memory unit='MiB'>{memory}</memory>
  <vcpu placement='static'>{core}</vcpu>
  <resource>
    <partition>/machine</partition>
  </resource>
  <os>
    <type arch='x86_64' machine='pc'>hvm</type>
    <boot dev='hd'/>
  </os>
  <features>
    <acpi/>
    <apic/>
    <pae/>
  </features>
  <cpu mode='host-model'>
    <model fallback='allow'/>
    <topology sockets='1' cores='{core}' threads='1'/>
  </cpu>
  <clock offset='localtime'/>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>destroy</on_crash>
  <devices>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2'/>
      <source file='{image}'/>
      <target dev='vda' bus='virtio'/>
    </disk>
    <emulator>/usr/libexec/qemu-kvm</emulator>
    <controller type='usb' index='0' model='ich9-ehci1'>
    </controller>
    <controller type='usb' index='0' model='ich9-uhci1'>
      <master startport='0'/>
    </controller>
    <controller type='usb' index='0' model='ich9-uhci2'>
      <master startport='2'/>
    </controller>
    <controller type='usb' index='0' model='ich9-uhci3'>
      <master startport='4'/>
    </controller>
    <controller type='pci' index='0' model='pci-root'>
    </controller>
    <controller type='virtio-serial' index='0'>
    </controller>
    <interface type='bridge'>
      <source bridge='virbr0'/>
      <model type='virtio'/>
    </interface>
    <channel type='spicevmc'>
      <target type='virtio' name='com.redhat.spice.0'/>
    </channel>
    <channel type='unix'>
      <source mode='bind' path='/var/lib/libvirt/qemu/{channel}'/>
      <target type='virtio' name='org.qemu.guest_agent.0'/>
    </channel>
    <input type='tablet' bus='usb'>
    </input>
    <input type='mouse' bus='ps2'/>
<!--
    <input type='keyboard' bus='ps2'/>
-->
    <graphics type='spice' autoport='yes' listen='0.0.0.0' keymap='en-us'>
      <listen type='address' address='0.0.0.0'/>
    </graphics>
    <sound model='ac97'>
    </sound>
    <video>
      <model type='qxl' ram='65536' vram='65536' vgamem='16384' heads='1'/>
    </video>
    <redirdev bus='usb' type='spicevmc'>
    </redirdev>
    <redirdev bus='usb' type='spicevmc'>
    </redirdev>
    <memballoon model='virtio'>
    </memballoon>
  </devices>
</domain>
'''

def _create_container_callback(container_id):
    cli = get_app().get_client()
    res = cli.get('/v1/containers/%s' % container_id)
    etag = res.json['_etag']

    res = cli.patch('/v1/containers/%s' % container_id,
                    headers={'If-Match': etag},
                    data={'status': 'stop'})


def on_inserted_containers(containers):
    cli = get_app().get_client()
    conn = open_libvirt_connection()

    for container in containers:
        res = cli.get('/v1/containers/%s?embedded={"application":1}' % str(container['_id']))
        container = res.json

        base_img = os.path.join(CONFIG['APPLICATION_IMAGE_HOME'],
                                '%s.qcow2' % container['application']['_id'])
        img = os.path.join(CONFIG['CONTAINER_IMAGE_HOME'],
                           '%s.qcow2' % container['_id'])
        cmd = 'qemu-img create -f qcow2 -b %s %s 500G' % (base_img, img)
        os.system(cmd)

        xml = KVM_INSTANCE_TEMPLATE.format(name=container['_id'],
                                           memory=container['application']['min_mem'],
                                           channel=container['_id'][:8],
                                           core=container['application']['min_core'],
                                           image=img)
        conn.defineXML(xml)
        task.spawn(_create_container_callback, str(container['_id']))

    conn.close()


def on_deleted_item_containers(container):
    channel_path = '/var/lib/libvirt/%s' % container['_id']
    if os.path.exists(channel_path):
        os.unlink(channel_path)

    conn = open_libvirt_connection()

    dom = conn.lookupByName(container['_id'])
    dom.undefine()

    conn.close()

    img = os.path.join(CONFIG['CONTAINER_IMAGE_HOME'], '%s.qcow2' % container['_id'])
    cmd = 'rm -f %s' % img
    os.system(cmd)


def _booting_container_callback(container_id):
    conn = open_libvirt_connection()

    try:
        dom = conn.lookupByName(container_id)
        channel_file = '/var/lib/libvirt/qemu/%s' % container_id[:8]
        if dom.info()[0] != 1 and os.path.exists(channel_file):
            os.unlink(channel_file)
        dom.create()
    except Exception as ex:
        pass
    finally:
        conn.close()

    cli = get_app().get_client()
    res = cli.get('/v1/containers/%s' % container_id)
    etag = res.json['_etag']

    res = cli.patch('/v1/containers/%s' % container_id,
                    headers={'If-Match': etag},
                    data={'status': 'starting'})


def _starting_container_callback(container_id):
    addr = PeerAgent.builder(container_id=container_id).get_local_address()
    assert addr

    cli = get_app().get_client()
    res = cli.get('/v1/containers/%s' % container_id)
    etag = res.json['_etag']

    volumes = []
    for v in res.json['volumes']:
        res = cli.get('/v1/volumes/%s' % v['volume'])
        volumes.append({'uri': res.json['uri'],
                        'drive': v['drive']})

    PeerAgent.builder(container_address=addr,
                      container_username='cloud',
                      container_password='asd').mount_drives(volumes)

    metadata = PeerAgent.builder(container_address=addr,
                                 container_username='cloud',
                                 container_password='asd').get_rdp_info()

    res = cli.patch('/v1/containers/%s' % container_id,
                    headers={'If-Match': etag},
                    data={'status': 'running',
                          'connection': {
                              'host': addr,
                              'port': 3389,
                              'username': 'cloud',
                              'password': 'asd',
                              'metadata': metadata}})


def _autoremove_container_callback(container_id):
    cli = get_app().get_client()

    while True:
        res = cli.get('/v1/containers/%s' % container_id)
        if res.json['status'] == 'stop':
            break
        task.sleep(1)

    _etag = res.json['_etag']
    cli.delete('/v1/containers/%s' % container_id, headers={'If-Match': _etag})


def _shutting_container_callback(container_id):
    conn = open_libvirt_connection()
    try:
        dom = conn.lookupByName(container_id)
        dom.destroy()
    except libvirtError as ex:
        pass
    finally:
        conn.close()

    cli = get_app().get_client()
    res = cli.get('/v1/containers/%s' % container_id)
    autoremove = res.json['autoremove']
    etag = res.json['_etag']
    res = cli.patch('/v1/containers/%s' % container_id,
                    headers={'If-Match': etag},
                    data={'status': 'stop',
                          'connection': {
                              'host': None,
                              'port': None,
                              'username': None,
                              'password': None,
                              'metadata': None}})

    if autoremove:
        task.spawn(_autoremove_container_callback, container_id)

def on_updated_containers(container, original):
    if 'status' in container:
        container_id = str(original['_id'])
        print "change container: %s status from %s to %s" % (str(original['_id']), original['status'], container['status'])
        _g = globals()
        cbfn = '_%s_container_callback' % container['status']
        if cbfn in _g:
            task.spawn(_g[cbfn], container_id)


def load_hook(app):
    app.on_inserted_containers += on_inserted_containers
    app.on_deleted_item_containers += on_deleted_item_containers
    app.on_updated_containers += on_updated_containers

    return app
