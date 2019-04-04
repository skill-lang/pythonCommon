from typing import Union

from common.internal.fieldTypes.IntegerTypes import Singleton
from common.internal.FieldType import FieldType
from common.streams.OutStream import OutStream


class BoolType(FieldType, Singleton):

    _typeID = 6

    def __init__(self):
        super(BoolType, self).__init__(self.typeID())

    def readSingleField(self, inStream):
        return inStream.bool()

    def calculateOffset(self, xs: Union[list, dict, set]):
        return len(xs)

    def singleOffset(self, x):
        return 1

    def writeSingleField(self, data, out: OutStream):
        out.bool(data is not None and data)

    def __str__(self):
        return "bool"
