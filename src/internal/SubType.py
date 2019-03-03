from src.internal.NamedType import NamedType
from src.internal.SkillObject import SkillObject


class SubType(SkillObject, NamedType):

    def __init__(self, tpool, skillID):
        super(SubType, self).__init__(skillID)
        self.tpool = tpool

    def skillName(self):
        return self.tpool.name

    def toString(self):
        return self.skillName() + "#" + self.skillID
