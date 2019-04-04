from common.internal.FieldType import FieldType
from common.internal.fieldTypes.IntegerTypes import Singleton
from typing import Union
from common.streams.FileInputStream import FileInputStream
from common.streams.FileOutputStream import FileOutputStream


class Float(FieldType, Singleton):
    
    def __init__(self, typeID):
        super(Float, self).__init__(typeID)

    def calculateOffset(self, xs: Union[dict, list, set, tuple]):
        return len(xs)


class F32(Float):

    def __init__(self):
        super(F32, self).__init__(12)

    def readSingleField(self, instream: FileInputStream):
        return instream.f32()

    def singleOffset(self, x):
        return 4

    def writeSingleField(self, target, outstream: FileOutputStream):
        if target is None:
            outstream.f32(0)
        else:
            outstream.f32(target)
    
    def calculateOffset(self, xs: Union[dict, list, set, tuple]):
        return 4 * super(F32, self).calculateOffset(xs)

    def __str__(self):
        return "f32"


class F64(Float):

    def __init__(self):
        super(F64, self).__init__(13)

    def readSingleField(self, instream: FileInputStream):
        return instream.f64()

    def singleOffset(self, x):
        return 8

    def writeSingleField(self, target, outstream: FileOutputStream):
        if target is None:
            outstream.f64(0)
        else:
            outstream.f64(target)
            
    def calculateOffset(self, xs: Union[dict, list, set, tuple]):
        return 8 * super(F64, self).calculateOffset(xs)

    def __str__(self):
        return "f64"
