from abc import ABC

from common.internal.FieldDeclaration import FieldDeclaration
from common.internal.KnownField import KnownField


class KnownDataField(FieldDeclaration, KnownField, ABC):
    """
    Superclass of non-auto fields in binding.
    """

    def __init__(self, fType, name, owner):
        super(KnownDataField, self).__init__(fType, name, owner)

    def _rbc(self, c, mis):
        blocks: [] = self.owner.blocks
        blockIndex = 0
        endBlock = c.blockCount
        while blockIndex < endBlock:
            b = blocks[blockIndex]
            blockIndex += 1
            i = b.bpo
            self._rsc(i, i + b.count, mis)
