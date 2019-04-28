from typing import Union

from common.internal.FieldType import FieldType
from common.internal.fieldTypes.IntegerTypes import V64


class MapType(FieldType):
    _typeID = 20

    def __init__(self, keyType, valueType):
        super(MapType, self).__init__(self.typeID())
        self.keyType = keyType
        self.valueType = valueType

    def readSingleField(self, inStream):
        i = inStream.v64()
        rval = {}
        while i != 0:
            i -= 1
            a = self.keyType.readSingleField(inStream)
            rval[a] = self.valueType.readSingleField(inStream)
        return rval

    def calculateOffset(self, xs: Union[list, dict, set]):
        result = 0
        for x in xs:
            size = len(x)
            if size == 0:
                result += 1
            else:
                result += V64().singleV64Offset(size) + self.keyType.calculateOffset(x.keys())
                result += self.valueType.calculateOffset(x.values())
        return result

    def singleOffset(self, x):
        if x is None:
            size = 0
        else:
            size = len(x)
        if size == 0:
            return 1
        return V64().singleV64Offset(len(x)) + self.keyType.calculateOffset(x.keys()) + self.valueType.calculateOffset(
            x.values())

    def writeSingleField(self, data, out):
        if data is None:
            size = 0
        else:
            size = len(data)
        if size == 0:
            out.i8(0)
            return
        out.v64(size)
        for e in data:
            self.keyType.writeSingleField(e, out)
            self.valueType.writeSingleField(data[e], out)

    def __str__(self):
        return "map<{}, {}>".format(self.keyType, self.valueType)

    def __eq__(self, obj):
        if isinstance(obj, MapType):
            return self.keyType.__eq__(obj.keyType) and self.valueType.__eq__(obj.valueType)
        return False
