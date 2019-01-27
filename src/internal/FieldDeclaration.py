from src.internal.LazyField import LazyField
from src.internal.Exceptions import *
from src.internal.SkillState import SkillState
from src.internal.StoragePool import StoragePool
from src.internal.fieldDeclarations import IgnoredField
from src.restrictions import FieldRestriction
from src.internal.FieldType import FieldType
from src.internal.Blocks import *
import abc
import threading

from src.streams.FileInputStream import FileInputStream
from src.streams.MappedInStream import MappedInStream


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

    def finish(self, barrier: threading.Semaphore, readErrors: [], inStream: FileInputStream):
        if isinstance(self, IgnoredField):
            return 0

        block = 0
        for c in self.dataChunks:
            blockCounter = block
            block += 1
            f = self
            SkillState.threadPool.submit(runningFunction(inStream, c, self, barrier, readErrors, blockCounter))
        return block


def runningFunction(fis: FileInputStream, c, f: FieldDeclaration, barrier: threading.Semaphore, readErrors: [],
                    blockCounter):
    ex: SkillException = None
    try:
        mis: MappedInStream = fis.map(0, c.begin)
        if isinstance(c, BulkChunk):
            f.rbc(c, mis)
        else:
            i = c.bpo  # c is SimpleChunk => c has bpo
            f.rsc(i, i + c.count, mis)

        if not mis.eof() and not isinstance(f, LazyField):
            ex = PoolSizeMismatchError(blockCounter, c.begin, c.end, f)
    except SkillException as s:
        ex = s
    except BufferError as b:
        ex = PoolSizeMismatchError(blockCounter, c.begin, c.end, f, b)
    except Exception as e:
        ex = SkillException("internal error: unexpected foreign exception", e)
    finally:
        barrier.release()
        if ex is not None:
            readErrors.append(ex)


class KnownField(dict):
    pass


class NamedType(abc.ABC):

    tPool = None
