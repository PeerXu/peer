#! /usr/bin/env python2.7
from platform import platform
from setuptools import setup
from setuptools import find_packages

if not platform().startswith('Linux'):
    requires = [
    ]
else:
    requires = [
        "eve>=0.5.3",
        "pymongo>=2.8.1",
        "libvirt-python>=1.2.9",
        "pywinrm==0.0.3"
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
