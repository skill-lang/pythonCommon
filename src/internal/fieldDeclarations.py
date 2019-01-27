import abc
from src.internal.FieldDeclaration import FieldDeclaration


class KnownField(abc.ABC): pass


class InterfaceField(abc.ABC): pass


class IgnoredField(abc.ABC):

    @abc.abstractmethod
    def read(self, inStream): pass


class AutoField(abc.ABC, FieldDeclaration, KnownField):

    def rsc(self, i, h, inStream):
        raise Exception("one can not read auto fields!")

    def rbc(self, last, inStream):
        raise Exception("one can not read auto fields!")

    def osc(self, i, end):
        raise Exception("one get the offset of an auto field!")

    def wsc(self, i, end, outStream):
        raise Exception("one can not write auto fields!")
