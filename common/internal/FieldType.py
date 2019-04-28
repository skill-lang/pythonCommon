from typing import Union


class FieldType:

    def __init__(self, typeID):
        self._typeID = typeID

    def typeID(self):
        return self._typeID

    def __eq__(self, obj):
        if isinstance(obj, FieldType):
            return obj.typeID() == self.typeID()
        return False

    def hashCode(self): return self.typeID()

    def readSingleField(self, inStream):
        pass

    def calculateOffset(self, xs: Union[list, dict, set]):
        pass

    def singleOffset(self, x):
        pass

    def writeSingleField(self, data, out):
        pass

    def __str__(self):
        pass
