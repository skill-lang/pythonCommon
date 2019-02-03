from abc import ABC, abstractmethod
from typing import *


class FieldType(ABC):

    def __init__(self, typeID):
        self.typeID = typeID

    def equals(self, obj):
        if isinstance(obj, FieldType):
            return obj.typeID() == self.typeID()
        return False

    def hashCode(self): return self.typeID

    @abstractmethod
    def readSingleField(self, inStream):
        pass

    @abstractmethod
    def calculateOffset(self, xs: Union[list, dict, set]):
        pass

    @abstractmethod
    def singleOffset(self, x):
        pass

    @abstractmethod
    def writeSingleField(self, data, out):
        pass

    @abstractmethod
    def toString(self):
        pass
