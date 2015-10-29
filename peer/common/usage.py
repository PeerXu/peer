import sys

def usage():
    sys.stdout.write('''Usage: %s [OPTIONS] action [arg ...]

Options:

    -h, --help                    print usage
    -D, --debug=false             start a peer server in debug mode
    -H, --host=127.0.0.1          peer service host
    -P, --port=11214              peer service port

Actions:

    ps                  list containers
    connect             connect to container
    commit              create a new application from container's change
    start               start a stopped container
    stop                stop a running container
    run                 run a new container
    rm                  remove a existed container
    applications        list applications
    build               build an application from a Peerfile
    volumes             list volumes
    cv                  create a new volume
    rmv                 remove a existed volume

''' % sys.argv[0])
    sys.exit(1)
