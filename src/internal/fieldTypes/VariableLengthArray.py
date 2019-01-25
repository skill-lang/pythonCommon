from src.internal.FieldType import FieldType
from src.internal.fieldTypes.SingleArgumentType import SingleArgumentType


class VariableLengthArray(SingleArgumentType):

    typeID = 17

    def __init__(self, groundType: FieldType):
        super(VariableLengthArray, self).__init__(self.typeID, groundType)

    def readSingleField(self, inStream):
        i = inStream.v32()
        rval = []
        while i != 0:
            i -= 1
            rval.append(self.groundType.readSingleField(inStream))

    def toString(self):
        return self.groundType.toString() + "[]"

    def equals(self, obj):
        if isinstance(obj, VariableLengthArray):
            return self.groundType.equals(obj.groundType)
        return False
