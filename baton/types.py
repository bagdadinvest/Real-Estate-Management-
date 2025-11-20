from typing import TypeVar

from baton.models import Collection, DataObject

# Type of iRODS entity
EntityType = TypeVar("EntityType", DataObject, Collection)

# Object type returned by the custom object mapper
CustomObjectType = TypeVar("CustomObjectType")
