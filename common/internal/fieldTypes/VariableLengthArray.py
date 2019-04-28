from common.internal.FieldType import FieldType
from common.internal.fieldTypes.SingleArgumentType import SingleArgumentType


class VariableLengthArray(SingleArgumentType):

    _typeID = 17

    def __init__(self, groundType: FieldType):
        super(VariableLengthArray, self).__init__(self.typeID(), groundType)

    def readSingleField(self, inStream):
        i = inStream.v64()
        rval = []
        while i != 0:
            i -= 1
            rval.append(self.groundType.readSingleField(inStream))

    def __str__(self):
        return self.groundType.__str__() + "[]"

    def __eq__(self, obj):
        if isinstance(obj, VariableLengthArray):
            return self.groundType.__eq__(obj.groundType)
        return False
