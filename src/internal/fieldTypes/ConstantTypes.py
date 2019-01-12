

class ConstantInteger:

    def __init__(self, value):
        self.value = value

    def value(self):
        return self.value


class ConstantI8(ConstantInteger):
    typeID = 0

    def toString(self):
        return "const i8 = []".format(self.value())

    def equals(self, obj):
        if isinstance(obj, ConstantI8):
            return obj.value() == self.value()
        return False


class ConstantI16(ConstantInteger):
    typeID = 1

    def toString(self):
        return "const i16 = []".format(self.value())

    def equals(self, obj):
        if isinstance(obj, ConstantI16):
            return obj.value() == self.value()
        return False


class ConstantI32(ConstantInteger):
    typeID = 2

    def toString(self):
        return "const i32 = []".format(self.value())

    def equals(self, obj):
        if isinstance(obj, ConstantI32):
            return obj.value() == self.value()
        return False


class ConstantI64(ConstantInteger):
    typeID = 3

    def toString(self):
        return "const i64 = []".format(self.value())

    def equals(self, obj):
        if isinstance(obj, ConstantI64):
            return obj.value() == self.value()
        return False


class ConstantV64(ConstantInteger):
    typeID = 4

    def toString(self):
        return "const v64 = []".format(self.value())

    def equals(self, obj):
        if isinstance(obj, ConstantV64):
            return obj.value() == self.value()
        return False
