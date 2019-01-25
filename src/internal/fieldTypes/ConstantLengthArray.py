from typing import Union
from src.internal.Exceptions import *
from src.internal.fieldTypes.SingleArgumentType import SingleArgumentType


class ConstantLengthArray(SingleArgumentType):

    typeID = 15

    def __init__(self, length, groundType):
        super(ConstantLengthArray, self).__init__(self.typeID, groundType)
        self.length = length

    def readSingleField(self, inStream):
        rval = []
        for i in range(self.length, 0, -1):
            rval.append(self.groundType.readSingleField(inStream))
        return rval

    def calculateOffset(self, xs: Union[list, dict, set]):
        result = 0
        for x in xs:
            result += self.groundType.calculateOffset(x)
        return result

    def singleOffset(self, x):
        return self.groundType.calculateOffset(x)

    def writeSingleField(self, elements, out):
        if len(elements) != self.length:
            raise Exception  # TODO IllegalArgumentException
        for e in elements:
            self.groundType.writeSingleField(e, out)

    def toString(self):
        return self.groundType.toString() + "[" + self.length + "]"

    def equals(self, obj):
        if isinstance(obj, ConstantLengthArray):
            return (self.length == len(obj)) and self.groundType.equals(obj.groundType)
        return False