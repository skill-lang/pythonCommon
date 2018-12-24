from abc import ABC
from typing import Generic, TypeVar

T = TypeVar('T')


class FieldType(ABC, Generic[T]):

    def __init__(self, typeID: int):
        self._typeID_ = typeID

    def typeID(self):
        return self.typeID

    def equals(self, obj):
        if isinstance(obj, FieldType):
            return obj.typeID() == self.typeID()
        return False
