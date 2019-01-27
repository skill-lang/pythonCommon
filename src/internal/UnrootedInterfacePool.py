from typing import Union

from src.internal.FieldType import FieldType
from src.internal.Iterator import InterfaceIterator


class UnrootedInterfacePool(FieldType):

    def __init__(self, name, superPool, *realizations):
        super(UnrootedInterfacePool, self).__init__(superPool.typeID)
        self.name = name
        self.superType = superPool
        self.realizations = realizations

    def size(self):
        rval = 0
        for p in self.realizations:
            rval += p.size()
        return rval

    def __iter__(self): return InterfaceIterator(self.realizations)

    def readSingleField(self, inStream): return super(UnrootedInterfacePool, self).readSingleField(inStream)

    def calculateOffset(self, xs: Union[list, dict, set]): return self.superType.calculateOffset(xs)

    def singleOffset(self, x): return self.superType.singleOffset(x)

    def writeSingleField(self, data, out): super(UnrootedInterfacePool, self).writeSingleField(data, out)

    def getType(self): return self.superType

    def toString(self): return self.name
