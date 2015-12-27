from peer.server.schemas import containers
from peer.server.schemas import applications
from peer.server.schemas import volumes
from peer.server.schemas import user

__MODULES__ = [containers, applications, volumes, user]


def load_schemas():
    schemas = {}
    for module in __MODULES__:
        schemas.update(module.SCHEMA)
    return schemas
