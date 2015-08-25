#! /usr/bin/env python2.7
from platform import platform
from setuptools import setup
from setuptools import find_packages

if platform().startswith('Windows'):
    requires = [
    ]
else:
    requires = [
        "eve>=0.5.3",
        "gevent>=1.0.2",
        "pymongo>=2.8.1",
        "libvirt-python>=1.2.9"
    ]

setup(
    name='peer',
    description='',
    version='0.0.1',
    packages=find_packages(),
    author='Peer Xu',
    author_email='pppeerxu@gmail.com',
    install_requires=requires,
    entry_points={
        'console_scripts': ['peer=peer.scripts.main:main']
    }
)
