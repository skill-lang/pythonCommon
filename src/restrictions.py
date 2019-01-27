import abc
from src.internal.fieldTypes.IntegerTypes import Singleton
from src.internal.Exceptions import *


class FieldRestriction(abc.ABC):

    @abc.abstractmethod
    def check(self, value): pass


class TypeRestriction(abc.ABC): pass


class NonNull(FieldRestriction, Singleton):

    def check(self, value):
        if value is None:
            raise SkillException("Null value violates @NonNull.")


class Range(FieldRestriction):

    def __init__(self, minValue, maxValue):
        self.min = minValue
        self.max = maxValue

    def check(self, value):
        if value < self.min or self.max < value:
            raise SkillException("{} is not in Range({}, {})".format(value, self.min, self.max))


def makeRestriction(typeID, inStream):
    if typeID == 7:
        return Range(inStream.i8(), inStream.i8())
    elif typeID == 8:
        return Range(inStream.i16(), inStream.i16())
    elif typeID == 9:
        return Range(inStream.i32(), inStream.i32())
    elif typeID == 10:
        return Range(inStream.i64(), inStream.i64())
    elif typeID == 11:
        return Range(inStream.v64(), inStream.v64())
    elif typeID == 12:
        return Range(inStream.f32(), inStream.f32())
    elif typeID == 13:
        return Range(inStream.f64(), inStream.f64())
    else:
        return None
