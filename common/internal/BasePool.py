import copy
from common.internal.Iterator import *
from common.internal.StoragePool import StoragePool


class BasePool(StoragePool):
    """The base of a type hierarchy"""

    def __init__(self, poolIndex, name, knownFields: [], autoFields: [], cls):
        super(BasePool, self).__init__(poolIndex, name, None, knownFields, autoFields, cls)
        self._owner = None

    def _performAllocations(self):
        """
        Allocates data and all instances for this pool and its sub-pools.
        """
        # allocate data and link it to sub pools
        data = [None for _ in range(0, self._cachedSize)]
        subs = TypeHierarchyIterator(self)
        for s in subs:
            s._data = data
        # allocate instances
        subs = TypeHierarchyIterator(self)
        for s in subs:
            for b in s.blocks:
                s._allocateInstances(b)

    def _compress(self, lbpoMap: []) -> None:
        """
        compress new instances into the data array and update skillIDs
        :param lbpoMap: list of lbpos
        :return:
        """
        # create our part of the lbpo map
        theNext = 0
        subs: TypeHierarchyIterator = TypeHierarchyIterator(self)
        for p in subs:
            lbpo = theNext
            lbpoMap[p.typeID() - 32] = theNext
            theNext += p.staticSize() - p._deletedCount
            for f in p._dataFields:
                f._resetChunks(lbpo, p._cachedSize)

        # make d smaller than data
        d = []
        toi: TypeOrderIterator = TypeOrderIterator(self)
        for i in toi:
            if i.skillID != 0:
                d.append(i)
                i.skillID = len(d)

        # update after compressing
        self._data = d
        subs = TypeHierarchyIterator(self)
        for s in subs:
            s._updateAfterCompress(lbpoMap)

    def _prepareAppend(self, lbpoMap: [], chunkMap: {}):
        """
        Update StoragePools, FieldDeclarations and SkillIDs before appending to a file.
        :param lbpoMap: list of the lbpos
        :param chunkMap: Dict of FieldDeclaration and chunks
        :return:
        """
        # update lbpoMap
        theNext = len(self._data)
        for p in TypeHierarchyIterator(self):
            lbpoMap[p.typeID() - 32] = theNext
            theNext += len(p.newObjects)
        newInstances = self._newDynamicInstances().hasNext()

        # check if we have to append at all
        if not newInstances and not (len(self.blocks) == 0) and not (len(self._dataFields) == 0):
            done = True
            for f in self._dataFields:
                if len(f.dataChunks) == 0:
                    done = False
                    break
            if done:
                return

        if newInstances:
            # if we have to resize
            d: [] = copy.deepcopy(self._data)
            newLength = len(self) - len(self._data)
            extension = [None for _ in range(0, newLength)]
            d.extend(extension)
            i = len(self._data)
            dnii: DynamicNewInstancesIterator = self._newDynamicInstances()
            for instance in dnii:
                d[i] = instance
                i += 1
                instance.skillID = i
            self._data = d

        thi: TypeHierarchyIterator = TypeHierarchyIterator(self)
        for t in thi:
            t.updateAfterPrepareAppend(lbpoMap, chunkMap)

    def owner(self):
        """
        :return: returns SkillState which owns this BasePool
        """
        return self._owner
