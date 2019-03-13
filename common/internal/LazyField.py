from common.internal.DistributedField import DistributedField
from common.internal.Blocks import SimpleChunk, BulkChunk
import threading


class LazyField(DistributedField):
    lock = threading.Lock()
    chunkMap = {}
    isLazy = True

    def __init__(self, fType, name, owner):
        super(LazyField, self).__init__(fType, name, owner)

    def load(self):
        for p in self.chunkMap:
            if p.count > 0:
                if isinstance(p, BulkChunk):
                    super(LazyField, self).rbc(p, self.chunkMap[p])
                else:
                    c = p
                    super(LazyField, self).rsc(c.begin, c.end, self.chunkMap[p])
        self.chunkMap = None

    def ensureLoaded(self):
        if self.chunkMap is not None:
            self.load()

    def rsc(self, i, h, inStream):
        with self.lock:
            self.chunkMap[SimpleChunk(i, h, 1, 1)] = inStream

    def rbc(self, c, inStream):
        with self.lock:
            self.chunkMap[c] = inStream

    def get(self, ref):
        if ref.skillID == -1:
            return self.newData.get(ref)
        if self.chunkMap is not None:
            self.load()
        return super(LazyField, self).get(ref)

    def set(self, ref, value):
        if ref.skillID == -1:
            self.newData[ref] = value
        else:
            if self.chunkMap is not None:
                super(LazyField, self).set(ref, value)
