import abc
from src.internal.StoragePool import StoragePool


class SkillObject(abc.ABC):

    def _init_(self, skillId):
        self.skillId = skillId

    @abc.abstractmethod
    def skillName(self):
        pass

    def isDeleted(self):
        return 0 == self.skillId


class SubType(SkillObject):
    
    def __init__(self, pool: StoragePool, skillID):
        super(SubType, self).__init__(skillID)
        self.pool: StoragePool = pool
