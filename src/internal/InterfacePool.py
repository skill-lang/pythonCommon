from typing import Union

from src.internal.Iterator import InterfaceIterator
from src.internal.FieldType import FieldType
from src.internal.fieldTypes.IntegerTypes import V64


class InterfacePool(FieldType):

    def __init__(self, name, superPool, *realizations):
        super(InterfacePool, self).__init__(superPool.typeID)
        self.name = name
        self.superPool = superPool
        self.realizations = realizations

    def size(self):
        rval = 0
        for p in self.realizations:
            rval += p.size()
        return rval

    def iterator(self):
        return InterfaceIterator(self.realizations)

    def readSingleField(self, inStream):
        index = inStream.v32() - 1
        data: [] = self.superPool.data
        if index < 0 or len(data) <= index:
            return None
        return data[index]

    def calculateOffset(self, xs: Union[list, dict, set]):
        if len(self.superPool.data) < 128:
            return len(xs)
        result = 0
        for x in xs:
            if x is None:
                result += 1
            else:
                result += V64().singleV64Offset(x.skillID)
        return result

    def singleOffset(self, x):
        if x is None:
            return 1
        else:
            return V64().singleV64Offset(x.skillID)

    def writeSingleField(self, data, out):
        if data is None:
            out.i8(0)
        else:
            out.v64(data.skillID)

    def toString(self):
        return self.name
