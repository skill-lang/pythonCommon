from common.internal.FieldType import FieldType
from common.internal.SkillObject import SkillObject
from common.internal.SubType import SubType
from common.internal.Iterator import TypeHierarchyIterator, StaticFieldIterator, StaticDataIterator, FieldIterator,\
    DynamicDataIterator, TypeOrderIterator, DynamicNewInstancesIterator
from common.internal.Exceptions import SkillException
from common.internal.LazyField import LazyField
from common.internal.Blocks import BulkChunk, Block, SimpleChunk
from common.internal.fieldTypes.IntegerTypes import V64
import threading
import copy
from abc import ABC, abstractmethod


class StoragePool(FieldType):

    dataFields = []
    noKnownFields = []
    noAutoFields = []
    lock = threading.Lock()

    def __init__(self, poolIndex: int, name: str, superPool, knownFields: [], autoFields):
        super(StoragePool, self).__init__(32 + poolIndex)
        self.name = name
        self.superPool: StoragePool = superPool
        if superPool is None:
            self.typeHierarchyHeight = 0
            self.basePool = self
        else:
            self.typeHierarchyHeight = superPool.typeHierarchyHeight + 1
            self.basePool = superPool.basePool
        self.knownFields = knownFields
        self.autoFields = autoFields

        self.cachedSize = 0
        self.basePool = None
        self.blocks = []
        self.staticDataInstances: int = 0
        self.nextPool = None
        self.newObjects = []
        self.data = []
        self.fixed = False
        self.deletedCount = 0

    def setNextPool(self, nx):
        self.nextPool = nx

    def nextPool(self):
        return self.nextPool

    @staticmethod
    def establishNextPool(types: []):
        L = []
        for i in range(len(types) - 1, -1, -1):
            t: StoragePool = types[i]
            p: StoragePool = t.superPool
            if p is None:
                continue

            ids = t.typeID() - 32
            if L[ids] is None:
                L[ids] = t

            if p.nextPool is None:
                L[p.typeID() - 32] = L[ids]
            else:
                L[ids].setNextPool(p.nextPool)
            p.setNextPool(t)

    def fields(self):
        return StaticFieldIterator(self)

    def allFields(self):
        return FieldIterator(self)

    def lastBlock(self) -> Block:
        return self.blocks[len(self.blocks) - 1]

    def newObject(self, index):
        return self.newObjects[index]

    def newDynamicInstancesIterator(self):
        return DynamicNewInstancesIterator(self)

    def newDynamicInstancesSize(self):
        rval = 0
        ts = TypeHierarchyIterator(self)
        while ts.hasNext():
            rval += len(ts.__next__().newObjects)
        return rval

    def staticSize(self):
        return self.staticDataInstances + len(self.newObjects)

    def staticInstances(self):
        return StaticDataIterator(self)

    def superName(self):
        if self.superPool is not None:
            return self.superPool.name
        else:
            return None

    def getByID(self, index: int):
        if len(self.data) < 1 or (len(self.data) - 1) <= index:
            return None
        return self.data[index]

    def readSingleField(self, instream):
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
                result += V64().singleV64Offset(x.skillID)
        return result

    def singleOffset(self, x: SkillObject):
        if x is None:
            return 1
        v = x.skillID
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

    def writeSingleField(self, data, out):
        if data is None:
            out.i8(0)
        else:
            out.v64(data.skillId)

    def size(self):
        if self.fixed:
            return self.cachedSize
        size = 0
        ts = TypeHierarchyIterator(self)
        while ts.hasNext():
            size += ts.__next__().staticSize()

    def toArray(self, a: []):
        rval: [] = copy.deepcopy(a)
        ddi = self.__iter__()
        for i in range(0, len(rval)):
            rval[i] = ddi.__next__()
        return rval

    def add(self, e: SkillObject):
        if self.fixed:
            raise Exception("can not fix a pool that contains new objects")
        self.newObjects.append(e)

    def delete(self, target: SkillObject):
        if not target.isDeleted():
            target.skillID = 0
            self.deletedCount += 1

    def owner(self):
        return self.basePool.owner()

    def __iter__(self) -> DynamicDataIterator:
        return DynamicDataIterator(self)

    def typeOrderIterator(self):
        return TypeOrderIterator(self)

    def allocateInstances(self, last: Block):
        i = last.bpo
        high = i + last.staticCount
        while i < high:
            self.data[i] = SubType(self, i + 1)
            i += 1

    def updateAfterCompress(self, lbpoMap: []):
        if self.basePool is not None:
            self.data = self.basePool._data
        else:
            self.data = None

        self.staticDataInstances += len(self.newObjects) - self.deletedCount
        self.deletedCount = 0
        self.newObjects.clear()
        self.blocks.clear()
        self.blocks.append(Block(lbpoMap[self.typeID - 32], self.cachedSize, self.staticDataInstances))

    def addField(self, fType: FieldType, name: str):
        return LazyField(fType, name, self)

    def addKnownField(self, name, string, annotation):
        raise Exception("Arbitrary storage pools know no fields!")

    def makeSubPool(self, index, name):
        return StoragePool(index, name, self, self.noKnownFields, self.noAutoFields)

    def updateAfterPrepareAppend(self, lbpoMap: [], chunkMap: {}):
        if self.basePool is not None:
            self.data = self.basePool._data
        else:
            self.data = None

        newInstances = self.newDynamicInstancesIterator().hasNext()
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
                    if len(f.dataChunks) == 0 and blockCount != 1:
                        c = BulkChunk(-1, -1, self.cachedSize, blockCount)
                    elif newInstances:
                        c = SimpleChunk(-1, -1, lbpo, lcount)
                    else:
                        continue

                    f.addChunk(c)
                    with self.lock:
                        chunkMap[f] = c

        self.newObjects.clear()

    def toString(self):
        return self.__name__

    class Builder(ABC):

        def __init__(self, pool, instance):
            self.pool = pool
            self.instance = instance

        @abstractmethod
        def make(self): pass
