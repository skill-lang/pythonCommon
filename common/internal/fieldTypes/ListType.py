from common.internal.FieldType import FieldType
from common.internal.fieldTypes.SingleArgumentType import SingleArgumentType


class ListType(SingleArgumentType):
    """
    Field type of all lists.
    """

    _typeID = 18

    def __init__(self, groundType: FieldType):
        super(ListType, self).__init__(self.typeID(), groundType)

    def readSingleField(self, inStream):
        rval = []
        for i in range(inStream.v64(), 0, -1):
            rval.append(self.groundType.readSingleField(inStream))
        return rval

    def __str__(self):
        return "list<" + self.groundType.__str__() + ">"

    def __eq__(self, obj):
        if isinstance(obj, ListType):
            return self.groundType.__eq__(obj.groundType)
        return False
