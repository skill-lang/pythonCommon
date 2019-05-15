from common.internal.Exceptions import SkillException, PoolSizeMismatchError
from common.internal.Blocks import BulkChunk, SimpleChunk
from abc import ABC, abstractmethod


class FieldDeclaration(ABC):

    isLazy = False
    isDistributed = False

    def __init__(self, fType, name, owner, isAuto=False):
        """
        :param fType: field type of field
        :param name: name of field
        :param owner: StoragePool which owns this FieldDeclaration
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
        """
        :return: name of this FieldDeclaration
        """
        return self._name

    def fieldType(self):
        """
        :return: class of this FieldDeclaration's field type
        """
        return self._fType

    def __str__(self):
        """
        :return: FieldDeclaration as a string
        """
        return str(self._fType) + " " + self._name

    def __eq__(self, obj):
        """
        Is executed if two objects are compared with '=='
        :param obj: object to compare with this one
        :return: True, iff name and field type are the same
        """
        if self == obj:
            return True
        if isinstance(obj, FieldDeclaration):
            return obj._name == self._name and obj._fType == self._fType
        return False

    def addChunk(self, chunk):
        """
        Chunk is added to this FieldDeclaration
        :param chunk: chunk to be added
        :return:
        """
        self._dataChunks.append(chunk)

    def _addOffsetToLastChunk(self, offset):
        """
        adds offset to last chunk of this FieldDeclaration
        :param offset: offset to be added
        :return: new end of chunk
        """
        c = self._lastChunk()
        c.begin += offset
        c.end += offset
        return c.end

    def _lastChunk(self):
        """
        :return: last chunk of this FieldDeclaration
        """
        return self._dataChunks[len(self._dataChunks) - 1]

    def _resetChunks(self, lbpo, newSize):
        """
        clears list of chunks of this FieldDeclaration
        :param lbpo:
        :param newSize:
        :return:
        """
        self._dataChunks.clear()
        self._dataChunks.append(SimpleChunk(-1, -1, lbpo, newSize))

    def _rsc(self, i, end, inStream):
        """
        Function to set the value of field of instances. Values are read from SimpleChunks. i and end define an interval.
        :param i: index of first instance
        :param end: index of first instance not to be read
        :param inStream: FileInputStream
        :return:
        """
        d = self.owner.data()
        for j in range(i, end):
            value = inStream.v64()
            setattr(d[j], self._name, value)

    @abstractmethod
    def _rbc(self, target, inStream):
        """
        Function to set the value of field of instances. Values are read from BulkChunks.
        :param target: BulkChunk
        :param inStream: FileInputStream
        :return:
        """
        pass

    @abstractmethod
    def _osc(self, i, end):
        """
        Calculates offset
        :param i:
        :param end:
        :return:
        """
        pass

    def _obc(self, c: BulkChunk):
        """
        Calculates offset differently by creating temporary SimpleChunks.
        :param c: BulkChunk
        :return:
        """
        blocks: [] = self.owner.blocks
        blockIndex = 0
        endBlock = c.blockCount
        while blockIndex < endBlock:
            b = blocks[blockIndex]
            blockIndex += 1
            i = b.bpo
            self._osc(i, i + b.count)

    def _wsc(self, i, end, outStream):
        """
        Writes field of instances i to (end-1) for SimpleChunks.
        :param i: first instance
        :param end: first instance not be written
        :param outStream: FileOutputStream
        :return:
        """
        d = self.owner.data()
        for j in range(i, end):
            value = getattr(d[j], self._name)
            outStream.v64(value)

    def _wbc(self, c: BulkChunk, outStream):
        """
        Writes field of instances for a BulkChunk by writing multiple SimpleChunks.
        :param c: BulkChunk
        :param outStream: FileOutputStream
        :return:
        """
        blocks: [] = self.owner.blocks
        blockIndex = 0
        endBlock = c.blockCount
        while blockIndex < endBlock:
            b = blocks[blockIndex]
            blockIndex += 1
            i = b.bpo
            self._wsc(i, i + b.count, outStream)

    def get(self, ref):
        """
        Get field of ref with this field's name.
        :param ref: SkillObject
        :return: value
        """
        assert hasattr(ref, self.name())
        return getattr(ref, self.name())

    def _finish(self, readErrors: [], inStream):
        """
        Finishes this FieldDeclaration by reading and assigning fields to the instances.
        :param readErrors: collection of errors
        :param inStream: FileInputStream
        :return: number of Chunks read
        """
        block = 0
        for c in self._dataChunks:
            blockCounter = block
            block += 1
            ex = None
            try:
                inStream.jump(c.begin)
                if isinstance(c, BulkChunk):
                    self._rbc(c, inStream)
                else:
                    i = c.bpo
                    self._rsc(i, i + c.count, inStream)
            except SkillException as s:
                ex = s
            except BufferError as b:
                ex = PoolSizeMismatchError(blockCounter, c.begin, c.end, self, b)
            except Exception as e:
                ex = SkillException("internal error: unexpected foreign exception", e)
            finally:
                if ex is not None:
                    readErrors.append(ex)
        return block
