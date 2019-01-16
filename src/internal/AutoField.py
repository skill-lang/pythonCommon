from typing import Generic, TypeVar, Any
from src.internal.SkillObject import SkillObject

T = TypeVar('T', bound=Any)
Obj = TypeVar('Obj', bound=SkillObject)


class AutoField(list):
    pass
