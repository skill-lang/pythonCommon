from src.internal.FieldDeclaration import *
from src.streams.MappedInStream import MappedInStream


class KnownDataField(FieldDeclaration, KnownField):

    def __init__(self, fType, name, owner):
        super(KnownDataField, self).__init__(fType, name, owner)

    def rbc(self, c, mis: MappedInStream):
        blocks: [] = self.owner.blocks
        blockIndex = 0
        endBlock = c.blockCount
        while blockIndex < endBlock:
            b = blocks[blockIndex]
            blockIndex += 1
            i = b.bpo
            # TODO rsc in FieldDeclaration
