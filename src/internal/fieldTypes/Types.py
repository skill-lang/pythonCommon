from abc import ABC
from src.internal.FieldType import FieldType
from src.streams.InStream import InStream


class I8(FieldType):
    """currently disabled"""

    typeID = 7

    def __init__(self):
        super(I8, self).__init__(self.typeID)
        self.instance = None

    def get(self):
        return self.instance

    @staticmethod
    def readSingleField(ins: InStream):
        return ins.i8()

    def calculateOffset(self):
        pass

    def singleOffset(self, x: int):
        pass
