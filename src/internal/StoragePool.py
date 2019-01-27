from src.internal.SkillObject import SkillObject, SubType
from src.internal.BasePool import BasePool
from src.internal.fieldDeclarations import AutoField
from src.streams.InStream import InStream
from src.internal.Iterator import *
from src.internal.Exceptions import *
from src.internal.LazyField import LazyField
from src.internal.Blocks import *
from src.internal.fieldTypes.IntegerTypes import *
import threading
import copy


class StoragePool(FieldType):

    dataFields = []
    noKnownFields = []
    noAutoFields: AutoField = AutoField()
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

        self.cachedSize: int = None
        self.basePool: BasePool = None
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
        for i in range(len(types), -1, -1):
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

    @staticmethod
    def fixPools(pools: []):
        for p in pools:
            p.cachedSize = p.staticSize() - p.deletedCount
            p.fixed = True

        for i in range(len(pools), -1, -1):
            p = pools[i]
            if p.superPool is not None:
                p.superPool.cachedSize += p.cachedSize

    @staticmethod
    def unfixPools(pools: []):
        for p in pools:
            p.fixed = False

    def superName(self):
        if self.superPool is not None:
            return self.superPool.name
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
                result += V64().singleOffset(x.skillID)
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

    def stream(self):
        pass

    def toArray(self, a: []):
        rval: [] = copy.deepcopy(a)
        ddi = self.iterator()
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

    def addField(self, fType: FieldType, name: str):
        return LazyField(fType, name, self)

    def addKnownField(self, name, string, annotation):
        raise Exception("Arbitrary storage pools know no fields!")

    def makeSubPool(self, index, name):
        return StoragePool(index, name, self, self.noKnownFields, self.noAutoFields)

    def updateAfterPrepareAppend(self, lbpoMap: [], chunkMap: {}):
        self.data = self.basePool.data
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
