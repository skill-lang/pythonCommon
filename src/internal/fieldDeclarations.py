import abc
from src.internal.FieldDeclaration import FieldDeclaration


class KnownField(abc.ABC): pass


class InterfaceField(abc.ABC): pass


class IgnoredField(abc.ABC):

    @abc.abstractmethod
    def read(self, inStream): pass


class AutoField(abc.ABC, FieldDeclaration, KnownField):

    def rsc(self, i, h, inStream):
        raise Exception  # TODO Exception

    def rbc(self, last, inStream):
        raise Exception  # TODO Exception

    def osc(self, i, end):
        raise Exception  # TODO Exception

    def wsc(self, i, end, outStream):
        raise Exception  # TODO Exception
