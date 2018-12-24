from typing import Generic, TypeVar
from src.internal.SkillObject import SkillObject
from src.internal.StoragePool import StoragePool

T = TypeVar('T', bound=SkillObject)


class BasePool(StoragePool[T, T]):
    pass
