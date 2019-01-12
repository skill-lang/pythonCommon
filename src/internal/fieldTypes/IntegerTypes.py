from src.streams.FileInputStream import FileInputStream
from src.streams.FileOutputStream import FileOutputStream
from typing import Union


class Singleton:

    __instance = None

    def __init__(self):
        if self.__instance is None:
            Singleton.__instance = self
        else:
            raise Exception("This class is a singleton")

    @staticmethod
    def get():
        if Singleton.__instance is None:
            Singleton()
        return Singleton.__instance


class Integer(Singleton):

    def __init__(self, typeID):
        super(Integer, self).__init__()
        self.typeID = typeID

    def calculateOffset(self, xs: Union[dict, list, set, tuple]):
        return len(xs)


class I8(Integer):
    
    def __init__(self):
        super(I8, self).__init__(7)

    def readSingleField(self, instream: FileInputStream):
        return instream.i8()

    def singleOffset(self):
        return 1

    def writeSingleField(self, target, outstream: FileOutputStream):
        if target is None:
            outstream.i8(0)
        else:
            outstream.i8(target)

    def toString(self):
        return "i8"


class I16(Integer):

    def __init__(self):
        super(I16, self).__init__(8)

    def readSingleField(self, instream: FileInputStream):
        return instream.i16()

    def singleOffset(self):
        return 2

    def writeSingleField(self, target, outstream: FileOutputStream):
        if target is None:
            outstream.i16(0)
        else:
            outstream.i16(target)

    def toString(self):
        return "i16"

    def calculateOffset(self, xs: Union[dict, list, set, tuple]):
        return 2 * super(I16, self).calculateOffset(xs)


class I32(Integer):

    def __init__(self):
        super(I32, self).__init__(9)

    def readSingleField(self, instream: FileInputStream):
        return instream.i32()

    def singleOffset(self):
        return 4

    def writeSingleField(self, target, outstream: FileOutputStream):
        if target is None:
            outstream.i32(0)
        else:
            outstream.i32(target)

    def toString(self):
        return "i32"
    
    def calculateOffset(self, xs: Union[dict, list, set, tuple]):
        return 4 * super(I32, self).calculateOffset(xs)


class I64(Integer):

    def __init__(self):
        super(I64, self).__init__(10)

    def readSingleField(self, instream: FileInputStream):
        return instream.i64()

    def singleOffset(self):
        return 8

    def writeSingleField(self, target, outstream: FileOutputStream):
        if target is None:
            outstream.i64(0)
        else:
            outstream.i64(target)

    def toString(self):
        return "i64"

    def calculateOffset(self, xs: Union[dict, list, set, tuple]):
        return 8 * super(I64, self).calculateOffset()
