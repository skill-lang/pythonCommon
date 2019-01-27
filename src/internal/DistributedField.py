from src.internal.FieldDeclaration import FieldDeclaration
from src.internal.FieldType import FieldType
from src.streams.MappedInStream import MappedInStream
from src.streams.MappedOutputStream import MappedOutputStream


class DistributedField(FieldDeclaration):

    def __init__(self, fType: FieldType, name, owner):
        super(DistributedField, self).__init__(fType, name, owner)
        self.data = {}
        self.newData = {}

    def check(self):
        for r in self.restrictions:
            for x in self.data.values():
                r.check(x)
            for x in self.newData.values():
                r.check(x)

    def rsc(self, i, h, inStream: MappedInStream):
        d: [] = self.owner.basePool.data
        for j in range(i, h):
            self.data[d[j]] = self.fType.readSingleField(inStream)

    def rbc(self, c, inStream: MappedInStream):
        d: [] = self.owner.basePool.data
        blocks: [] = self.owner.blocks
        blockIndex = 0
        endBlock = c.blockCount
        while blockIndex < endBlock:
            b = blocks[blockIndex]
            blockIndex += 1
            i = b.bpo
            for j in range(i , i + b.count):
                self.data[d[j]] = self.fType.readSingleField(inStream)

    def compress(self):
        self.data.update(self.newData)
        self.newData.clear()

    def osc(self, i, h):
        d: [] = self.owner.basePool.data
        rval = 0
        for j in range(i, h):
            rval += self.fType.singleOffset(self.data.get(d[j]))
        # offset += rval

    def wsc(self, i, h, out: MappedOutputStream):
        d: [] = self.owner.basePool.data
        for j in range(i, h):
            self.fType.writeSingleField(self.data.get(d[j]), out)

    def get(self, ref):
        if ref.skillID == -1:
            return self.newData[ref]
        return self.data.get(ref)

    def set(self, ref, value):
        if ref.skillID == -1:
            self.newData[ref] = value
        else:
            self.data[ref] = value
