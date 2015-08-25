import os

PEER_HOME = '/home/cloud/peer'

CONTAINER_HOME = os.path.join(PEER_HOME, 'containers')
CONTAINER_IMAGE_HOME = os.path.join(CONTAINER_HOME, 'images')

APPLICATION_HOME = os.path.join(PEER_HOME, 'applications')
APPLICATION_IMAGE_HOME = os.path.join(APPLICATION_HOME, 'images')
