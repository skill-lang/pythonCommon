import abc

from src.internal.FieldDeclaration import NamedType
from src.internal.StoragePool import StoragePool


class SkillObject(abc.ABC):

    def _init_(self, skillId):
        self.skillID = skillId

    @abc.abstractmethod
    def skillName(self):
        pass

    def isDeleted(self):
        return 0 == self.skillID


class SubType(SkillObject, NamedType):

    def __init__(self, tpool: StoragePool, skillID):
        super(SubType, self).__init__(skillID)
        self.tpool: StoragePool = tpool

    def skillName(self):
        return self.tpool.name

    def toString(self):
        return self.skillName() + "#" + self.skillID
