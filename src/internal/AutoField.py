from src.internal.FieldDeclaration import FieldDeclaration
from src.internal.KnownField import KnownField


class AutoField(FieldDeclaration, KnownField):

    def rsc(self, i, h, inStream):
        raise Exception("one can not read auto fields!")

    def rbc(self, last, inStream):
        raise Exception("one can not read auto fields!")

    def osc(self, i, end):
        raise Exception("one get the offset of an auto field!")

    def wsc(self, i, end, outStream):
        raise Exception("one can not write auto fields!")
