import abc


class SkillObject(abc.ABC):

    def _init_(self, skillId):
        self.skillId = skillId

    @abc.abstractmethod
    def skillName(self):
        pass

