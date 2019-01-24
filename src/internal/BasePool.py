from typing import Generic, TypeVar
from src.internal.SkillObject import SkillObject
from src.internal.StoragePool import StoragePool
from src.internal.Iterator import *
import copy


class BasePool(StoragePool, list):

    def __init__(self, poolIndex, name, knownFields: [], autoFields):
        super(BasePool, self).__init__(poolIndex, name, None, knownFields, autoFields)

    def newArray(self):
        return []

    def performAllocations(self):
        pass
        # TODO stuff with semaphor

    def compress(self, lbpoMap: []):
        # create our part of the lbpo map
        next = 0
        subs: TypeHierarchyIterator = TypeHierarchyIterator(self)
        while subs.hasNext():
            p: StoragePool = subs.__next__()
            lbpo = lbpoMap[p.typeID() - 32] = next
            next += p.staticSize() - p.deletedCount
            for f in p.dataFields:
                f.resetChunks(lbpo, p.cachedSize)

        # make d smaller than data
        d = []
        p = 0
        toi: TypeOrderIterator = TypeOrderIterator(self)
        while toi.hasNext():
            i = toi.__next__()
            if i.skillID != 0:
                d[p] = i
                p += 1
                i.skillID = p

        # update after compressing
        self.data = d
        subs = TypeHierarchyIterator(self)
        while subs.hasNext():
            subs.__next__().updateAfterCompress(lbpoMap)

    def prepareAppend(self, lbpoMap: [], chunkMap: {}):
        # update lbpoMap
        next = len(self.data)
        for p in TypeHierarchyIterator(self):
            lbpoMap[p.typeID - 32] = next
            next += len(p.newObjects)
        newInstances = self.newDynamicInstancesIterator().hasNext()

        # check if we have to append at all
        if not newInstances and not (len(self.blocks) == 0) and not (len(self.dataFields) == 0):
            done  = True
            for f in self.dataFields:
                if len(f.dataChunks) == 0:
                    done = False
                    break
            if done:
                return

        if newInstances:
            # if we have to resize
            d: [] = copy.deepcopy(self.data)
            i = len(self.data)
            dnii: DynamicNewInstancesIterator = self.newDynamicInstancesIterator()
            while dnii.hasNext():
                instance = dnii.__next__()
                d[i] = instance
                i += 1
                instance.skillID = i
            self.data = d

        thi: TypeHierarchyIterator = TypeHierarchyIterator(self)
        while thi.hasNext():
            thi.__next__().updateAfterPrepareAppend(lbpoMap, chunkMap)
