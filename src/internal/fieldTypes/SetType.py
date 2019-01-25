from src.internal.FieldType import FieldType
from src.internal.fieldTypes.SingleArgumentType import SingleArgumentType


class SetType(SingleArgumentType):

    typeID = 19

    def __init__(self, groundType: FieldType):
        super(SetType, self).__init__(self.typeID, groundType)

    def readSingleField(self, inStream):
        i = inStream.v32()
        rval = set()
        while i != 0:
            rval.add(self.groundType.readSingleField(inStream))
        return rval

    def toString(self):
        return "set<" + self.groundType.toString() + ">"

    def equals(self, obj):
        if isinstance(obj, SetType):
            return self.groundType.equals(obj.groundType)
        return False
