from typing import Union

from src.internal.FieldType import FieldType
from src.internal.fieldTypes.IntegerTypes import V64


class SingleArgumentType(FieldType):

    def __init__(self, typeID, groundType: FieldType):
        super(SingleArgumentType, self).__init__(typeID)
        self.groundType = groundType

    def calculateOffset(self, xs: Union[list, dict, set]):
        result = 0
        for x in xs:
            if x is None:
                size = 0
            else:
                size = len(x)
            if size == 0:
                result += 1
            else:
                result += V64().singleV64Offset(size)
                result += self.groundType.calculateOffset(x)

    def singleOffset(self, x):
        if x is None:
            return 1
        return V64().singleV64Offset(len(x) + self.groundType.calculateOffset(x))

    def writeSingleField(self, x, out):
        if x is None:
            size = 0
        else:
            size = len(x)
        if size == 0:
            out.i8(0)
        else:
            out.v64(size)
            for e in x:
                self.groundType.writeSingleField(e, out)
