from typing import Generic, TypeVar
from src.internal.FieldType import FieldType
from src.internal.SkillObject import SkillObject

B = TypeVar('B', bound=SkillObject)
T = TypeVar('T', bound=SkillObject)


class StoragePool(FieldType, Generic[T, B]):
    pass
