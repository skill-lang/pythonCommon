from common.internal.FieldType import FieldType
from common.internal.SkillObject import SkillObject
from common.internal.Iterator import TypeHierarchyIterator, StaticFieldIterator, StaticDataIterator, FieldIterator,\
    DynamicDataIterator, TypeOrderIterator, DynamicNewInstancesIterator
from common.internal.Exceptions import SkillException
from common.internal.LazyField import LazyField
from common.internal.Blocks import BulkChunk, Block, SimpleChunk
from common.internal.fieldTypes.IntegerTypes import V64
import copy
from abc import ABC, abstractmethod


class StoragePool(FieldType):
    """
    A StoragePool exists for each class specified in the specification. It holds each instance of this class and
    manages all information and fields of it.
    """

    noKnownFields = []
    noAutoFields = []

    def __init__(self, poolIndex: int, name: str, superPool, knownFields: [], autoFields: [], cls):
        super(StoragePool, self).__init__(32 + poolIndex)
        self._name = name
        self.superPool: StoragePool = superPool
        if superPool is None:
            self.typeHierarchyHeight = 0
            self.basePool = self
        else:
            self.typeHierarchyHeight = superPool.typeHierarchyHeight + 1
            self.basePool = superPool.basePool
        self.knownFields = knownFields
        self._autoFields = autoFields

        self._cachedSize = 0
        self.blocks = []
        self.staticDataInstances: int = 0
        self._nextPool = None
        self.newObjects = []
        self._data = []
        self._dataFields = []
        self._fixed = False
        self._deletedCount = 0
        # classes
        self._cls = cls

    def __setNextPool(self, nx):
        """
        Sets the _nextPool of this StoragePool.
        :param nx: new next pool
        :return:
        """
        self._nextPool = nx

    def nextPool(self):
        """
        :return: _nextPool of this StoragePool
        """
        return self._nextPool

    def name(self):
        """
        :return: name of this StoragePool
        """
        return self._name

    def data(self):
        """
        :return: data array of this StoragePool
        """
        return self._data

    @staticmethod
    def _establishNextPool(types: []):
        """
        Sets _nextPool for all StoragePools in types. The StoragePools will be traversed in Pre-order.
        :param types: list of all StoragePools
        :return:
        """
        L = [None for i in range(0, len(types))]
        for i in range(len(types) - 1, -1, -1):
            t: StoragePool = types[i]
            p: StoragePool = t.superPool
            if p is None:
                continue

            ids = t.typeID() - 32
            if L[ids] is None:
                L[ids] = t

            if p.nextPool() is None:
                L[p.typeID() - 32] = L[ids]
            else:
                L[ids].__setNextPool(p.nextPool())
            p.__setNextPool(t)

    def fields(self):
        """
        :return: StaticFieldIterator over all FieldDeclarations of this StoragePool.
        """
        return StaticFieldIterator(self)

    def allFields(self):
        """
        :return: FieldIterator over all FieldDeclarations of this StoragePool and its superpools.
        """
        return FieldIterator(self)

    def lastBlock(self) -> Block:
        """
        :return: last block stored in this StoragePool
        """
        return self.blocks[len(self.blocks) - 1]

    def newObject(self, index):
        """
        :param index: index of the instance in the array which stores all newly created instances
        :return: instance stored at index in this array
        """
        return self.newObjects[index]

    def _newDynamicInstances(self):
        """
        :return: DynamicDataIterator over all instances of the StoragePools which are iterated in Pre-order.
        """
        return DynamicNewInstancesIterator(self)

    def _newDynamicInstancesSize(self):
        """
        :return: number of all newly created instances
        """
        rval = 0
        ts = TypeHierarchyIterator(self)
        for t in ts:
            rval += len(t.newObjects)
        return rval

    def staticSize(self):
        """
        :return: number of all instances stored in this StoragePool. 'Deleted' instances are counted as well.
        """
        return self.staticDataInstances + len(self.newObjects)

    def staticInstances(self):
        """
        :return: StaticDataIterator over all instances in this StoragePool.
        """
        return StaticDataIterator(self)

    def superName(self):
        """
        :return: name of the superpool.
        """
        if self.superPool is not None:
            return self.superPool.name()
        else:
            return None

    def getByID(self, index: int):
        """
        :param index: index of the instance
        :return: instance stored in the specified index by the data array
        """
        index -= 1
        if index < 0 or len(self._data) <= index:
            return None
        return self._data[index]

    def readSingleField(self, instream):
        """
        Reads index of instance hold by this StoragePool
        :param instream: FileInputStream
        :return: instance
        """
        index = instream.v64() - 1
        if (index < 0) or (len(self._data) <= index):
            return None
        return self._data[index]

    def calculateOffset(self, xs: []):
        """
        Calculates offset of list filled with instances
        :param xs: list
        :return: calculated offset
        """
        if len(self._data) < 128:
            return len(xs)
        result = 0
        for x in xs:
            if x is None:
                result += 1
            else:
                result += V64().singleV64Offset(x.skillID)
        return result

    def singleOffset(self, x: SkillObject):
        """
        Calculates offset of a single instance.
        :param x: instance
        :return: calculated offset
        """
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
        """
        Writes the SkillID of instance to the file.
        :param data: instance
        :param out: FileOutputStream
        :return:
        """
        if data is None:
            out.i8(0)
        else:
            out.v64(data.skillID)

    def __len__(self):
        """
        :return: size of this StoragePool or number of instances hold by this StoragePool.
        """
        if self._fixed:
            return self._cachedSize
        size = 0
        ts = TypeHierarchyIterator(self)
        for t in ts:
            size += t.staticSize()

    def toList(self, a: []):
        """
        Fill a copy of a list with instances
        :param a: list
        :return: filled list
        """
        rval: [] = copy.deepcopy(a)
        ddi = self.__iter__()
        for i in range(0, len(rval)):
            rval[i] = ddi.__next__()
        return rval

    def add(self, e: SkillObject):
        """
        Adds instance to this StoragePool
        :param e: instance to add
        :return:
        """
        if self._fixed:
            raise Exception("can not fix a pool that contains new objects")
        self.newObjects.append(e)

    def delete(self, target: SkillObject):
        """
        Delete instance from this StoragePool by setting the SkillID to 0.
        :param target: instance to delete
        :return:
        """
        if not target.isDeleted():
            target.skillID = 0
            self._deletedCount += 1

    def owner(self):
        """
        :return: SkillState which holds this StoragePool
        """
        return self.basePool.owner()

    def __iter__(self) -> DynamicDataIterator:
        """
        :return: DynamicDataIterator over all instances
        """
        return DynamicDataIterator(self)

    def typeOrderIterator(self):
        """
        :return: TypeOrderIterator over all instances in StoragePools in type order
        """
        return TypeOrderIterator(self)

    def _allocateInstances(self, last: Block):
        """
        Creates instances from the binary file.
        :param last: Block which stores the number of instances
        :return:
        """
        i = last.bpo
        high = i + last.staticCount
        if self._cls is not None:
            for j in range(i, high):
                self._data[j] = self._cls(j + 1)

    def _updateAfterCompress(self, lbpoMap: []):
        """
        :param lbpoMap:
        :return:
        """
        self._data = self.basePool.data()

        self.staticDataInstances += len(self.newObjects) - self._deletedCount
        self._deletedCount = 0
        self.newObjects.clear()
        self.blocks.clear()
        self.blocks.append(Block(lbpoMap[self.typeID() - 32], self._cachedSize, self.staticDataInstances))

    def addField(self, fType: FieldType, name: str):
        """
        Adds new FieldDeclaration to this StoragePool
        :param fType: Field type of the new field
        :param name: name of the new field
        :return: new LazyField
        """
        return LazyField(fType, name, self)

    def addKnownField(self, name, string, annotation):
        """
        Used by binding only!
        :param name:
        :param string:
        :param annotation:
        :return:
        """
        raise Exception("Arbitrary storage pools know no fields!")

    def makeSubPool(self, index, name, cls):
        """
        creates a new Subpool of this pool
        :param index: index of the new pool
        :param name: name of the new pool
        :param cls: class of the new pool
        :return: new StoragePool
        """
        return StoragePool(index, name, self, self.noKnownFields, self.noAutoFields, cls)

    def updateAfterPrepareAppend(self, lbpoMap: [], chunkMap: {}):
        """
        Updates lbpo, blocks and chunks. Invoked by BasePool after 'prepare append'.
        :param lbpoMap: list of lbpos
        :param chunkMap: dict of FieldDeclarations and chunks
        :return:
        """
        if self.basePool is not None:
            self._data = self.basePool.data
        else:
            self._data = None

        it = self._newDynamicInstances()
        newInstances = it.index != it.last
        newPool = (len(self.blocks) == 0)

        exists = False
        for f in self._dataFields:
            if len(f.dataChunks) == 0:
                exists = True
                break
        newField = exists

        if newPool or newInstances or newField:
            lcount = self._newDynamicInstancesSize()
            if lcount == 0:
                lbpo = 0
            else:
                lbpo = lbpoMap[self.typeID() - 32]
            self.blocks.append(Block(lbpo, lcount, len(self.newObjects)))
            blockCount = len(self.blocks)
            self.staticDataInstances += len(self.newObjects)

            if newInstances or not newPool:
                for f in self._dataFields:
                    if f.index == 0:
                        continue
                    if len(f.dataChunks) == 0 and blockCount != 1:
                        c = BulkChunk(-1, -1, self._cachedSize, blockCount)
                    elif newInstances:
                        c = SimpleChunk(-1, -1, lbpo, lcount)
                    else:
                        continue

                    f.addChunk(c)
                    chunkMap[f] = c

        self.newObjects.clear()

    def __str__(self):
        """
        :return: string representation of this StoragePool
        """
        return self._name

    class Builder(ABC):

        def __init__(self, pool, instance):
            self.pool = pool
            self.instance = instance

        @abstractmethod
        def make(self): pass
