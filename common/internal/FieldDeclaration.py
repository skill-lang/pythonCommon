from common.internal.Exceptions import SkillException, PoolSizeMismatchError
from common.internal.Blocks import BulkChunk, SimpleChunk
import threading
from common.internal.threadpool import threadPool


class FieldDeclaration:

    isLazy = False
    isDistributed = False

    def __init__(self, fType, name, owner, index=-1):
        super(FieldDeclaration, self).__init__()
        self.fType = fType
        self.name = name

        self.owner = owner
        self.owner.dataFields.append(self)
        if index == -1:
            self.index = len(self.owner.dataFields)
        else:
            self.owner.autoFields[-index] = self

        self.dataChunks = []

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

    def rsc(self, i, end, inStream):
        pass

    def rbc(self, target, inStream):
        pass

    def osc(self, i, end):
        pass

    def obc(self, c: BulkChunk):
        blocks: [] = self.owner.blocks
        blockIndex = 0
        endBlock = c.blockCount
        while blockIndex < endBlock:
            b = blocks[blockIndex]
            blockIndex += 1
            i = b.bpo
            self.osc(i, i + b.count)

    def wsc(self, i, end, outStream):
        pass

    def wbc(self, c: BulkChunk, outStream):
        blocks: [] = self.owner.blocks
        blockIndex = 0
        endBlock = c.blockCount
        while blockIndex < endBlock:
            b = blocks[blockIndex]
            blockIndex += 1
            i = b.bpo
            self.wsc(i, i + b.count, outStream)

    def finish(self, barrier: threading.Semaphore, readErrors: [], inStream):
        block = 0
        for c in self.dataChunks:
            blockCounter = block
            block += 1
            threadPool.submit(runningFunction(inStream, c, self, barrier, readErrors, blockCounter))
        return block


def runningFunction(fis, c, f: FieldDeclaration, barrier: threading.Semaphore, readErrors: [],
                    blockCounter):
    ex: SkillException = None
    try:
        mis = fis.map(0, c.begin)
        if isinstance(c, BulkChunk):
            f.rbc(c, mis)
        else:
            i = c.bpo  # c is SimpleChunk => c has bpo
            f.rsc(i, i + c.count, mis)

        if not mis.eof() and not f.isLazy:
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
