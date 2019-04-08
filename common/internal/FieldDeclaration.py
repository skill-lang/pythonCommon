from common.internal.Exceptions import SkillException, PoolSizeMismatchError
from common.internal.Blocks import BulkChunk, SimpleChunk
import threading
from abc import ABC, abstractmethod


class FieldDeclaration(ABC):

    isLazy = False
    isDistributed = False

    def __init__(self, fType, name, owner, isAuto=False):
        """
        :param fType: field type of field
        :param name: name of field
        :param owner: storagepool which owns this field declaration
        :param isAuto: is this field an auto field
        """
        super(FieldDeclaration, self).__init__()
        self._fType = fType
        self._name = name
        self.owner = owner
        if not isAuto:
            self.owner._dataFields.append(self)
        self._index = len(self.owner._dataFields)
        self._offset = 0
        self._dataChunks = []

    def name(self):
        return self._name

    def fieldType(self):
        return self._fType

    def __str__(self):
        return str(self._fType) + " " + self._name

    def equals(self, obj):
        if self == obj:
            return True
        if isinstance(obj, FieldDeclaration):
            return obj._name == self._name and obj._fType == self._fType
        return False

    def addChunk(self, chunk):
        self._dataChunks.append(chunk)

    def _addOffsetToLastChunk(self, offset):
        c = self._lastChunk()
        c.begin += offset
        c.end += offset
        return c.end

    def _lastChunk(self):
        return self._dataChunks[len(self._dataChunks) - 1]

    def _resetChunks(self, lbpo, newSize):
        self._dataChunks.clear()
        self._dataChunks.append(SimpleChunk(-1, -1, lbpo, newSize))

    def _rsc(self, i, end, inStream):
        d = self.owner.data()
        for j in range(i, end):
            value = inStream.v64()
            setattr(d[j], self._name, value)

    @abstractmethod
    def _rbc(self, target, inStream):
        pass

    @abstractmethod
    def _osc(self, i, end):
        pass

    def _obc(self, c: BulkChunk):
        blocks: [] = self.owner.blocks
        blockIndex = 0
        endBlock = c.blockCount
        while blockIndex < endBlock:
            b = blocks[blockIndex]
            blockIndex += 1
            i = b.bpo
            self._osc(i, i + b.count)

    def _wsc(self, i, end, outStream):
        d = self.owner.data()
        for j in range(i, end):
            value = getattr(d[j], self._name)
            outStream.v64(value)

    def _wbc(self, c: BulkChunk, outStream):
        blocks: [] = self.owner.blocks
        blockIndex = 0
        endBlock = c.blockCount
        while blockIndex < endBlock:
            b = blocks[blockIndex]
            blockIndex += 1
            i = b.bpo
            self._wsc(i, i + b.count, outStream)

    def get(self, ref):
        assert hasattr(ref, self.name())
        return getattr(ref, self.name())

    def _finish(self, barrier: threading.Semaphore, readErrors: [], inStream):
        block = 0
        for c in self._dataChunks:
            blockCounter = block
            block += 1
            a = inStream.file.tell()
            ex = None
            try:
                inStream.jump(c.begin)
                if isinstance(c, BulkChunk):
                    self._rbc(c, inStream)
                else:
                    i = c.bpo  # c is SimpleChunk => c has bpo
                    self._rsc(i, i + c.count, inStream)
            except SkillException as s:
                ex = s
            except BufferError as b:
                ex = PoolSizeMismatchError(blockCounter, c.begin, c.end, self, b)
            except Exception as e:
                ex = SkillException("internal error: unexpected foreign exception", e)
            finally:
                barrier.release()
                if ex is not None:
                    readErrors.append(ex)
        return block
