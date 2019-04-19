from common.internal.NamedType import NamedType
from common.internal.SkillObject import SkillObject


class SubType(SkillObject, NamedType):

    def __init__(self, tpool, skillID):
        super(SubType, self).__init__(skillID)
        self.tpool = tpool

    def skillName(self):
        return self.tpool.name()

    def __str__(self):
        return self.skillName() + "#" + self.skillID
