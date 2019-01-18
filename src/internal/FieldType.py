import abc
from typing import *


class FieldType(abc.ABC, list):

    def __init__(self, typeID):
        super(FieldType, self).__init__()
        self.typeID = typeID

    def typeID(self):
        return self.typeID

    def equals(self, obj):
        if isinstance(obj, FieldType):
            return obj.typeID() == self.typeID()
        return False

    @abc.abstractmethod
    def readSingleField(self, inStream):
        pass

    @abc.abstractmethod
    def calculateOffset(self, xs: Union[list, dict, set]):
        pass

    @abc.abstractmethod
    def singleOffset(self, x):
        pass

    @abc.abstractmethod
    def writeSingleField(self, data, out):
        pass

    @abc.abstractmethod
    def toString(self):
        pass
