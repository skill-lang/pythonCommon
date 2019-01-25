from src.internal.fieldTypes.SingleArgumentType import SingleArgumentType


class ListType(SingleArgumentType):

    typeID = 18

    def readSingleField(self, inStream):
        rval = []
        for i in range(inStream.v32(), 0, -1):
            rval.append(self.groundType.readSingleField(inStream))
        return rval

    def toString(self):
        return "list<" + self.groundType.toString() + ">"

    def equals(self, obj):
        if isinstance(obj, ListType):
            return self.groundType.equals(obj.groundType)
        return False
