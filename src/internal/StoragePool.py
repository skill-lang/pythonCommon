from src.internal.SkillObject import SkillObject, SubType
from src.internal.BasePool import BasePool
from src.internal.Blocks import Block
from src.internal.AutoField import AutoField
from src.streams.InStream import InStream
from src.streams.OutStream import OutStream
from src.internal.Exceptions import *
from threading import Lock
import copy


class StoragePool(FieldType, dict):

    dataFields = []
    noKnownFields = []
    noAutoFields: AutoField = AutoField()

    def __init__(self, poolIndex: int, name: str, superPool, knownFields: [], autoFields):
        super(StoragePool, self).__init__(32 + poolIndex)
        self.__name__ = name
        self.superPool: StoragePool = superPool
        if superPool is None:
            self.typeHierarchyHeight = 0
            self.basePool = self
        else:
            self.typeHierarchyHeight = superPool.typeHierarchyHeight + 1
            self.basePool = superPool.basePool
        self.knownFields = knownFields
        self.autoFields = autoFields

        self.cachedSize: int = None
        self.basePool: BasePool = None
        self.blocks = []
        self.staticDataInstances: int = 0
        self._nextPool_: StoragePool
        self.newObjects = []
        self.data = []
        self.__fixed__ = False
        self.deletedCount = 0

    def __setNextPool__(self, nx):
        self._nextPool_ = nx

    def nextPool(self):
        return self._nextPool_

    @staticmethod
    def establishNextPool(types: []):
        L = []
        for i in range(len(types), -1, -1):
            t: StoragePool = types[i]
            p: StoragePool = t.superPool
            if p is None:
                continue

            ids = t.typeID() - 32
            if L[ids] is None:
                L[ids] = t

            if p._nextPool_ is None:
                L[p.typeID() - 32] = L[ids]
            else:
                L[ids].__setNextPool__(p._nextPool_)
            p.__setNextPool__(t)

    def fields(self):
        """TODO: StaticFieldIterator? override"""
        pass

    def allFields(self):
        """TODO: FieldIterator? override"""
        pass

    def lastBlock(self) -> Block:
        return self.blocks[len(self.blocks) - 1]

    def newObject(self, index):
        return self.newObjects[index]

    def newDynamicInstances(self):
        """TODO: DynamicNewInstancesIterator?"""
        pass

    def newDynamicInstancesSize(self):
        rval = 0
        # TODO TypeHierarchyIterator?
        return rval

    def staticSize(self):
        return self.staticDataInstances + len(self.newObjects)

    def staticInstances(self):
        """TODO StaticDataIterator"""
        pass

    def fixed(self):
        return self.__fixed__

    @staticmethod
    def fixedPools(pools: []):
        for p in pools:
            p.cachedSize = p.staticSize() - p.deletedCount
            p.__fixed__ = True

        for i in range(len(pools), -1, -1):
            p = pools[i]
            if p.superPool is not None:
                p.superPool.cachedSize += p.cachedSize

    @staticmethod
    def unfixPools(pools: []):
        for p in pools:
            p.__fixed__ = False

    def name(self):
        return self.__name__

    def superName(self):
        if self.superPool is not None:
            return self.superPool.name()
        else:
            return None

    def getByID(self, index: int):
        if len(self.data) < 1 or (len(self.data) - 1) <= index:
            return None
        return self.data[index]

    def readSingleField(self, instream: InStream):
        index = instream.v32() - 1
        if (index < 0) or (len(self.data) <= index):
            return None
        return self.data[index]

    def calculateOffset(self, xs: []):
        if len(self.data) < 128:
            return len(xs)
        result = 0
        for x in xs:
            if x is None:
                result += 1
            else:
                result += 0 # TODO add V64.singleV64Offset(x.skillID)
        return result

    @staticmethod
    def singleOffset(x: SkillObject):
        if x is None:
            return 1
        v = x.skillId
        if (v & 0xFFFFFF80) == 0:
            return 1
        elif (v & 0xFFFFC000) == 0:
            return 2
        elif (v & 0xFFE00000) == 0:
            return 3
        elif (v & 0xF0000000) == 0:
            return 4
        else:
            return 5

    @staticmethod
    def writeSingleField(ref: SkillObject, out: OutStream):
        if ref is None:
            out.i8(0)
        else:
            out.v64(ref.skillId)

    def size(self):
        if self.fixed():
            return self.cachedSize
        size = 0
        # TODO TypeHierarchyIterator?

    def toArray(self, a: []):
        rval: [] = copy.deepcopy(a)
        # TODO DynamicDataIterator

    def add(self, e: SkillObject):
        if self.fixed():
            raise Exception("can not fix a pool that contains new objects")
        self.newObjects.append(e)

    def delete(self, target: SkillObject):
        if not target.isDeleted():
            target.skillId = 0
            self.deletedCount += 1

    def owner(self):
        return self.basePool.owner()

    def iterator(self):
        # TODO: DynamicDataIterator
        pass

    def typeOrderIterator(self):
        # TODO: TypeOrderIterator
        pass

    def make(self):
        raise SkillException("We prevent reflective creation of new instances, because it is bad style!")

    def allocateInstances(self, last: Block):
        i = last.bpo
        high = i + last.staticCount
        while i < high:
            self.data[i] = SubType(self, i + 1)
            i += 1

    def updateAfterCompress(self, lbpoMap: []):
        self.data = self.basePool.data
        self.staticDataInstances += len(self.newObjects) - self.deletedCount
        self.deletedCount = 0
        self.newObjects.clear()
        self.blocks.clear()
        self.blocks.append(Block(lbpoMap[self.typeID() - 32], self.cachedSize, self.staticDataInstances))

    def addField(self, type: FieldType, name: str):
        pass

    def addKnownField(self, name, string, annotation):
        raise Exception("Arbitrary storage pools know no fields!")

    def makeSubPool(self, index, name):
        return StoragePool(index, name, self, self.noKnownFields, self.noAutoFields)

    def updateAfterPrepareAppend(self, lbpoMap: [], chunkMap: {}):
        self.data = self.basePool.data
        newInstances = self.newDynamicInstances().hasNext()
        newPool = (len(self.blocks) == 0)

        exists = False
        for f in self.dataFields:
            if len(f.dataChunks) == 0:
                exists = True
                break
        newField = exists

        if newPool or newInstances or newField:
            lcount = self.newDynamicInstancesSize()
            if lcount == 0:
                lbpo = 0
            else:
                lbpo = lbpoMap[self.typeID() - 32]
            self.blocks.append(Block(lbpo, lcount, len(self.newObjects)))
            blockCount = len(self.blocks)
            self.staticDataInstances += len(self.newObjects)

            if newInstances or not newPool:
                for f in self.dataFields:
                    if f.index == 0:
                        continue
                    c = None
                    if len(f.dataChunks) == 0 and blockCount != 1:
                        # TODO: new BulkChunk
                        pass
                    elif newInstances:
                        # TODO: new SimpleChunk
                        pass
                    else:
                        continue

                    f.addChunk(c)

                    lock = Lock()
                    lock.acquire()
                    chunkMap[f] = c
                    lock.release()

        self.newObjects.clear()

    def toString(self):
        return self.__name__
