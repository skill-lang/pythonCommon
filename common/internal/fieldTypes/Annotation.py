from typing import Union

from common.internal.FieldType import FieldType
from common.internal.fieldTypes.IntegerTypes import V64
from common.internal.NamedType import NamedType


class Annotation(FieldType):

    _typeID = 5

    def __init__(self, types):
        super(Annotation, self).__init__(self.typeID())
        self.types = types
        if self.types is None:
            raise Exception("Annotation.types shouldn't be None")
        self.typeByName: {} = None

    def fixTypes(self, poolByName):
        assert self.typeByName is None
        self.typeByName = poolByName

    def readSingleField(self, inStream):
        t = inStream.v64()
        f = inStream.v64()
        if t == 0:
            return None
        return self.types[t-1].getByID(f)

    def calculateOffset(self, xs: Union[list, dict, set]):
        result = 0
        for ref in xs:
            if ref is None:
                result += 2
            else:
                if isinstance(ref, NamedType):
                    result += V64().singleV64Offset(ref.tPool.typeID() - 31)
                else:
                    result += V64().singleV64Offset(self.typeByName[ref.skillName()].typeID() - 31)
                result += V64().singleV64Offset(ref.getSkillID())
        return result

    def singleOffset(self, x):
        if x is None:
            return 2
        if isinstance(x, NamedType):
            name = V64().singleV64Offset(x.tPool.typeID() - 31)
        else:
            name = V64().singleV64Offset(self.typeByName[x.skillName()].typeID() - 31)
        return name + V64().singleV64Offset(x.getSkillID())

    def writeSingleField(self, data, out):
        if data is None:
            out.i16(0)
            return

        if isinstance(data, NamedType):
            out.v64(data.tPool.typeID() - 31)
        else:
            out.v64(self.typeByName[data.skillName()].typeID() - 31)
        out.v64(data.getSkillID())

    def __str__(self):
        return "annotation"
