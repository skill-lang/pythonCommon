from typing import Generic, TypeVar
from src.internal.SkillObject import SkillObject
from src.internal.StoragePool import StoragePool


class BasePool(StoragePool, list):

    def __init__(self, poolIndex, name, knownFields: [], autoFields):
        super(BasePool, self).__init__(poolIndex, name, None, knownFields, autoFields)

    def performAllocations(self):
        pass
        # TODO stuff with semaphor

    def compress(self, lbpoMap: []):
        pass # TODO

    def prepareAppend(self, lbpoMap: [], chunkMap: {}):
        pass # TODO
