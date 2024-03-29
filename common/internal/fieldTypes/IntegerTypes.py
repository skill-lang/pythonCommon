from common.internal.FieldType import FieldType
from common.streams.FileInputStream import FileInputStream
from common.streams.FileOutputStream import FileOutputStream
from typing import Union


class Singleton(object):
    """
    Superclass of all classes which should be singletons.
    """
    _instance = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instance:
            cls._instance[cls] = super(Singleton, cls).__new__(cls)
        return cls._instance[cls]


class Integer(FieldType, Singleton):
    """
    Superclass of all non-constant integer types.
    """

    def __init__(self, typeID):
        super(Integer, self).__init__(typeID)

    def calculateOffset(self, xs: Union[dict, list, set, tuple]):
        return len(xs)


class I8(Integer):
    """
    Field type of all 8-bit integers.
    """
    
    def __init__(self):
        super(I8, self).__init__(7)

    def readSingleField(self, instream: FileInputStream):
        return instream.i8()

    def singleOffset(self, x):
        return 1

    def writeSingleField(self, target, outstream: FileOutputStream):
        if target is None:
            outstream.i8(0)
        else:
            outstream.i8(target)

    def __str__(self):
        return "i8"


class I16(Integer):
    """
    Field type of all 16-bit integers.
    """

    def __init__(self):
        super(I16, self).__init__(8)

    def readSingleField(self, instream: FileInputStream):
        return instream.i16()

    def singleOffset(self, x):
        return 2

    def writeSingleField(self, target, outstream: FileOutputStream):
        if target is None:
            outstream.i16(0)
        else:
            outstream.i16(target)

    def __str__(self):
        return "i16"

    def calculateOffset(self, xs: Union[dict, list, set, tuple]):
        return 2 * super(I16, self).calculateOffset(xs)


class I32(Integer):
    """
    Field type of all 32-bit integers.
    """

    def __init__(self):
        super(I32, self).__init__(9)

    def readSingleField(self, instream: FileInputStream):
        return instream.i32()

    def singleOffset(self, x):
        return 4

    def writeSingleField(self, target, outstream: FileOutputStream):
        if target is None:
            outstream.i32(0)
        else:
            outstream.i32(target)

    def __str__(self):
        return "i32"
    
    def calculateOffset(self, xs: Union[dict, list, set, tuple]):
        return 4 * super(I32, self).calculateOffset(xs)


class I64(Integer):
    """
    Field type of all 64-bit integers.
    """

    def __init__(self):
        super(I64, self).__init__(10)

    def readSingleField(self, instream: FileInputStream):
        return instream.i64()

    def singleOffset(self, x):
        return 8

    def writeSingleField(self, target, outstream: FileOutputStream):
        if target is None:
            outstream.i64(0)
        else:
            outstream.i64(target)

    def __str__(self):
        return "i64"

    def calculateOffset(self, xs: Union[dict, list, set, tuple]):
        return 8 * super(I64, self).calculateOffset(xs)


class V64(Integer):
    """
    Field type of all integers with variable length.
    """

    def __init__(self):
        super(V64, self).__init__(11)

    def readSingleField(self, instream: FileInputStream):
        return instream.v64()

    def singleOffset(self, ref):
        if ref is None:
            v = 0
        else:
            v = ref
        if (v & 0xFFFFFFFFFFFFFF80) == 0:
            return 1
        elif (v & 0xFFFFFFFFFFFFC000) == 0:
            return 2
        elif (v & 0xFFFFFFFFFFE00000) == 0:
            return 3
        elif (v & 0xFFFFFFFFF0000000) == 0:
            return 4
        elif (v & 0xFFFFFFF800000000) == 0:
            return 5
        elif (v & 0xFFFFFC0000000000) == 0:
            return 6
        elif (v & 0xFFFE000000000000) == 0:
            return 7
        elif (v & 0xFF00000000000000) == 0:
            return 8
        else:
            return 9

    def writeSingleField(self, target, outstream: FileOutputStream):
        if target is None:
            outstream.v64(0)
        else:
            outstream.v64(target)

    def __str__(self):
        return "v64"

    def calculateOffset(self, xs: Union[dict, list, set, tuple]):
        result = 0
        for v in xs:
            if (v & 0xFFFFFFFFFFFFFF80) == 0:
                result += 1
            elif (v & 0xFFFFFFFFFFFFC000) == 0:
                result += 2
            elif (v & 0xFFFFFFFFFFE00000) == 0:
                result += 3
            elif (v & 0xFFFFFFFFF0000000) == 0:
                result += 4
            elif (v & 0xFFFFFFF800000000) == 0:
                result += 5
            elif (v & 0xFFFFFC0000000000) == 0:
                result += 6
            elif (v & 0xFFFE000000000000) == 0:
                result += 7
            elif (v & 0xFF00000000000000) == 0:
                result += 8
            else:
                result += 9
        return result

    @staticmethod
    def singleV64Offset(v):
        """
        Special function to calculate offset faster.
        :param v:
        :return:
        """
        if (v & 0xFFFFFFFFFFFFFF80) == 0:
            return 1
        elif (v & 0xFFFFFFFFFFFFC000) == 0:
            return 2
        elif (v & 0xFFFFFFFFFFE00000) == 0:
            return 3
        elif (v & 0xFFFFFFFFF0000000) == 0:
            return 4
        elif (v & 0xFFFFFFF800000000) == 0:
            return 5
        elif (v & 0xFFFFFC0000000000) == 0:
            return 6
        elif (v & 0xFFFE000000000000) == 0:
            return 7
        elif (v & 0xFF00000000000000) == 0:
            return 8
        else:
            return 9
