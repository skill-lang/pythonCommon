from typing import Union
from common.internal.FieldType import FieldType


class ConstantInteger(FieldType):

    def __init__(self, typeID, value):
        super(ConstantInteger, self).__init__(typeID)
        self.value = value

    def readSingleField(self, inStream):
        return self.value

    def calculateOffset(self, xs: Union[list, dict, set]):
        return 0  # nothing to do

    def singleOffset(self, x):
        return 0  # nothing to do

    def writeSingleField(self, data, out):
        pass  # nothing to do


class ConstantI8(ConstantInteger):

    _typeID = 0

    def __init__(self, value):
        super(ConstantI8, self).__init__(self.typeID(), value)

    def __str__(self):
        return "const i8 = []".format(self.value())

    def equals(self, obj):
        if isinstance(obj, ConstantI8):
            return obj.value() == self.value()
        return False


class ConstantI16(ConstantInteger):

    _typeID = 1

    def __init__(self, value):
        super(ConstantI16, self).__init__(self.typeID(), value)

    def __str__(self):
        return "const i16 = []".format(self.value())

    def equals(self, obj):
        if isinstance(obj, ConstantI16):
            return obj.value() == self.value()
        return False


class ConstantI32(ConstantInteger):

    _typeID = 2

    def __init__(self, value):
        super(ConstantI32, self).__init__(self.typeID(), value)

    def __str__(self):
        return "const i32 = []".format(self.value())

    def equals(self, obj):
        if isinstance(obj, ConstantI32):
            return obj.value() == self.value()
        return False


class ConstantI64(ConstantInteger):

    _typeID = 3

    def __init__(self, value):
        super(ConstantI64, self).__init__(self.typeID(), value)

    def __str__(self):
        return "const i64 = []".format(self.value())

    def equals(self, obj):
        if isinstance(obj, ConstantI64):
            return obj.value() == self.value()
        return False


class ConstantV64(ConstantInteger):

    _typeID = 4

    def __init__(self, value):
        super(ConstantV64, self).__init__(self.typeID(), value)

    def __str__(self):
        return "const v64 = []".format(self.value())

    def equals(self, obj):
        if isinstance(obj, ConstantV64):
            return obj.value() == self.value()
        return False
