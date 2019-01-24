from src.internal.DistributedField import DistributedField
from src.streams.MappedInStream import MappedInStream
from src.internal.Blocks import *


class LazyField(DistributedField):
    
    chunkMap = {}

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

    def check(self):
        if self.chunkMap is None:
            super(LazyField, self).check()

    def rsc(self, i, h, inStream: MappedInStream):
        # TODO synchronized
        self.chunkMap[SimpleChunk(i, h, 1, 1)] = inStream

    def rbc(self, c, inStream: MappedInStream):
        # TODO synchronized
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
