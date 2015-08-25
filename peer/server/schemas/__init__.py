from peer.server.schemas import containers
from peer.server.schemas import applications
from peer.server.schemas import volumes

__MODULES__ = [containers, applications, volumes]

def load_schemas():
    schemas = {}
    for module in __MODULES__:
        schemas.update(module.SCHEMA)
    return schemas
