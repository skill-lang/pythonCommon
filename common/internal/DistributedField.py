from common.internal.FieldDeclaration import FieldDeclaration


class DistributedField(FieldDeclaration):
    """
    The fields data is distributed into an array (for now its a hash map) holding its instances.
    """

    isDistributed = True

    def __init__(self, fType, name, owner):
        super(DistributedField, self).__init__(fType, name, owner)
        self.data = {}
        self.newData = {}

    def rsc(self, i, h, inStream):
        d: [] = self.owner.basePool.data()
        for j in range(i, h):
            self.data[d[j]] = self.fType.readSingleField(inStream)

    def rbc(self, c, inStream):
        d: [] = self.owner.basePool.data()
        blocks: [] = self.owner.blocks
        blockIndex = 0
        endBlock = c.blockCount
        while blockIndex < endBlock:
            b = blocks[blockIndex]
            blockIndex += 1
            i = b.bpo
            for j in range(i, i + b.count):
                self.data[d[j]] = self.fType.readSingleField(inStream)

    def compress(self):
        """
        compress this field
        Note: for now, deleted elements can survive in data
        """
        self.data.update(self.newData)
        self.newData.clear()

    def osc(self, i, h):
        d: [] = self.owner.basePool.data()
        rval = 0
        for j in range(i, h):
            rval += self.fType.singleOffset(self.data.get(d[j]))
        # offset += rval

    def wsc(self, i, h, out):
        d: [] = self.owner.basePool.data()
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
