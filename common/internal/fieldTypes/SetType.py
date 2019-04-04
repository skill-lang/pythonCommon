from common.internal.FieldType import FieldType
from common.internal.fieldTypes.SingleArgumentType import SingleArgumentType


class SetType(SingleArgumentType):

    _typeID = 19

    def __init__(self, groundType: FieldType):
        super(SetType, self).__init__(self.typeID(), groundType)

    def readSingleField(self, inStream):
        i = inStream.v64()
        rval = set()
        while i != 0:
            rval.add(self.groundType.readSingleField(inStream))
        return rval

    def __str__(self):
        return "set<" + self.groundType.__str__() + ">"

    def equals(self, obj):
        if isinstance(obj, SetType):
            return self.groundType.equals(obj.groundType)
        return False
