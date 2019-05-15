from common.internal.FieldDeclaration import FieldDeclaration


class DistributedField(FieldDeclaration):
    """
    The fields data is distributed into an array (for now its a hash map) holding its instances.
    """

    isDistributed = True

    def __init__(self, fType, name, owner):
        super(DistributedField, self).__init__(fType, name, owner)
        self._data = {}
        self._newData = {}

    def _rsc(self, i, h, inStream):
        d: [] = self.owner.basePool.data()
        for j in range(i, h):
            self._data[d[j]] = self._fType.readSingleField(inStream)

    def _rbc(self, c, inStream):
        d: [] = self.owner.basePool.data()
        blocks: [] = self.owner.blocks
        blockIndex = 0
        endBlock = c.blockCount
        while blockIndex < endBlock:
            b = blocks[blockIndex]
            blockIndex += 1
            i = b.bpo
            for j in range(i, i + b.count):
                self._data[d[j]] = self._fType.readSingleField(inStream)

    def _compress(self):
        """
        compress this field
        """
        self._data.update(self._newData)
        self._newData.clear()

    def _osc(self, i, h):
        d: [] = self.owner.basePool.data()
        rval = 0
        for j in range(i, h):
            rval += self._fType.singleOffset(self._data.get(d[j]))
        # offset += rval

    def _wsc(self, i, h, out):
        d: [] = self.owner.basePool.data()
        for j in range(i, h):
            self._fType.writeSingleField(self._data.get(d[j]), out)

    def get(self, ref):
        if ref.skillID == -1:
            return self._newData[ref]
        return self._data.get(ref)

    def set(self, ref, value):
        if ref.skillID == -1:
            self._newData[ref] = value
        else:
            self._data[ref] = value
