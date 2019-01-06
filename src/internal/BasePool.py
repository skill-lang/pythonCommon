from typing import Generic, TypeVar
from src.internal.SkillObject import SkillObject
from src.internal.StoragePool import StoragePool


class BasePool(StoragePool, list):
    pass
