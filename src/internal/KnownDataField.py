from src.internal.FieldDeclaration import FieldDeclaration, KnownField


class KnownDataField(FieldDeclaration, KnownField):

    def __init__(self, fType, name, owner):
        super(KnownDataField, self).__init__(fType, name, owner)

    def rbc(self, c, mis):
        blocks: [] = self.owner.blocks
        blockIndex = 0
        endBlock = c.blockCount
        while blockIndex < endBlock:
            b = blocks[blockIndex]
            blockIndex += 1
            i = b.bpo
            self.rsc(i, i + b.count, mis)
