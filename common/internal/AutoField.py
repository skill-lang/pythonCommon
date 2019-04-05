from common.internal.FieldDeclaration import FieldDeclaration
from common.internal.KnownField import KnownField


class AutoField(FieldDeclaration, KnownField):

    def __init__(self, fType, name, owner, index):
        super(AutoField, self).__init__(fType, name, owner, True)
        self._index = index
        self.owner._autoFields[-index] = self

    def _rsc(self, i, h, inStream):
        raise Exception("one can not read auto fields!")

    def _rbc(self, last, inStream):
        raise Exception("one can not read auto fields!")

    def _osc(self, i, end):
        raise Exception("one get the offset of an auto field!")

    def _wsc(self, i, end, outStream):
        raise Exception("one can not write auto fields!")
