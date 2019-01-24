from src.internal.StoragePool import StoragePool
from src.internal.FieldRestriction import FieldRestriction
from src.internal.FieldType import FieldType
from src.internal.Blocks import *
import abc


class FieldDeclaration(dict, abc.ABC):

    def __init__(self, fType: FieldType, name, owner: StoragePool, index=-1):
        super(FieldDeclaration, self).__init__()
        self.fType = fType
        self.name = name

        self.owner: StoragePool = owner
        self.owner.dataFields.append(self)
        if index == -1:
            self.index = len(self.owner.dataFields)
        else:
            self.owner.autoFields[-index] = self

        self.restrictions = set()
        self.dataChunks = []

    def addRestriction(self, r: FieldRestriction):
        self.restrictions.add(r)

    def check(self):
        if len(self.restrictions) != 0:
            for x in self.owner:
                if not x.isDeleted():
                    for r in self.restrictions:
                        r.check(self.get(x))

    def toString(self):
        return self.fType.toString() + " " + self.name

    def equals(self, obj):
        if self == obj:
            return True
        if isinstance(obj, FieldDeclaration):
            return obj.name == self.name and obj.fType == self.fType
        return False

    def addChunk(self, chunk):
        self.dataChunks.append(chunk)

    def addOffsetToLastChunk(self, offset):
        c = self.lastChunk()
        c.begin += offset
        c.end += offset
        return c.end

    def lastChunk(self):
        return self.dataChunks[len(self.dataChunks) - 1]

    def resetChunks(self, lbpo, newSize):
        self.dataChunks.clear()
        self.dataChunks.append(SimpleChunk(-1, -1, lbpo, newSize))

    @abc.abstractmethod
    def rsc(self, i, end, inStream):
        pass

    @abc.abstractmethod
    def rbc(self, target, inStream):
        pass

    @abc.abstractmethod
    def osc(self, i, end):
        pass

    def obc(self, c: BulkChunk):
        blocks: [] = self.owner.blocks
        blockIndex = 0
        endBlock = c.blockCount
        while blockIndex < endBlock:
            b: Block = blocks[blockIndex]
            blockIndex += 1
            i = b.bpo
            self.osc(i, i + b.count)

    @abc.abstractmethod
    def wsc(self, i, end, outStream):
        pass

    def wbc(self, c: BulkChunk, outStream):
        blocks: [] = self.owner.blocks
        blockIndex = 0
        endBlock = c.blockCount
        while blockIndex < endBlock:
            b: Block = blocks[blockIndex]
            blockIndex += 1
            i = b.bpo
            self.wsc(i, i + b.count, outStream)

    # TODO finish() because sth with semaphor


class KnownField(dict):
    pass


class NamedType(abc.ABC):

    @abc.abstractmethod
    def τPool(self):
        pass
