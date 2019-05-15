from typing import Union

from common.internal.FieldType import FieldType
from common.internal.fieldTypes.IntegerTypes import V64


class Annotation(FieldType):
    """
    Field type class of Annotations. Annotations are saved in variable annotationTypes of the SkillState.
    """

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
                result += V64().singleV64Offset(self.typeByName[ref.skillName].typeID() - 31)
                result += V64().singleV64Offset(ref.getSkillID())
        return result

    def singleOffset(self, x):
        if x is None:
            return 2
        name = V64().singleV64Offset(self.typeByName[x.skillName].typeID() - 31)
        return name + V64().singleV64Offset(x.getSkillID())

    def writeSingleField(self, data, out):
        if data is None:
            out.i16(0)
            return
        out.v64(self.typeByName[data.skillName].typeID() - 31)
        out.v64(data.getSkillID())

    def __str__(self):
        return "annotation"
