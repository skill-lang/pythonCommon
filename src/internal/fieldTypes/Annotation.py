from typing import Union

from src.internal.FieldType import FieldType
from src.internal.fieldTypes.IntegerTypes import V64
from src.internal.FieldDeclaration import NamedType


class Annotation(FieldType):

    typeID = 5

    def __init__(self, types):
        super(Annotation, self).__init__(self.typeID)
        self.types = types
        if self.types is None:
            raise Exception("Annotation.types shouldn't be None")
        self.typeByName: {} = None

    def fixTypes(self, poolByName):
        if self.typeByName is None:
            raise Exception("Annotation.typeByName shouldn't be None")
        self.typeByName = poolByName

    def readSingleField(self, inStream):
        t = inStream.v32()
        f = inStream.v32()
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
                    result += V64().singleOffset(ref.tPool.typeID - 31)
                else:
                    result += V64().singleOffset(self.typeByName[ref.skillName()].typeID - 31)
                result += V64().singleOffset(ref.getSkillID())
        return result

    def singleOffset(self, x):
        if x is None:
            return 2
        if isinstance(x, NamedType):
            name = V64().singleOffset(x.tPool.typeID - 31)
        else:
            name = V64().singleOffset(self.typeByName[x.skillName()].typeID - 31)
        return name + V64().singleOffset(x.getSkillID())

    def writeSingleField(self, data, out):
        if data is None:
            out.i16(0)
            return

        if isinstance(data, NamedType):
            out.v64(data.tPool.typeID() - 31)
        else:
            out.v64(self.typeByName[data.skillName()].typeID - 31)
        out.v64(data.getSkillID())

    def toString(self):
        return "annotation"
