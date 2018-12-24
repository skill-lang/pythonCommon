from typing import Generic, TypeVar
from src.internal.FieldType import FieldType
from src.internal.SkillObject import SkillObject
from src.internal.BasePool import BasePool
from src.internal.parts.Block import Block

B = TypeVar('B', bound=SkillObject)
T = TypeVar('T', bound=SkillObject)


class StoragePool(FieldType, Generic[T, B]):

    def __init__(self, poolIndex: int, name: str, superPool, knownFields: [], autoFields):
        super(StoragePool, self).__init__(32 + poolIndex)
        self.name = name
        self.superPool = superPool
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

    def lastBlock(self) -> Block:
        return self.blocks[self.blocks.__len__() - 1]
