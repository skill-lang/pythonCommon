from abc import ABC
from typing import Generic, TypeVar

T = TypeVar('T')


class FieldType(ABC, Generic[T]):
    pass
