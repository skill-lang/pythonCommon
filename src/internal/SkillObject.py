import abc

from src.internal.FieldDeclaration import NamedType
from src.internal.StoragePool import StoragePool


class SkillObject(abc.ABC):

    skillName = None

    def _init_(self, skillId):
        self.skillID = skillId

    def isDeleted(self):
        return 0 == self.skillID

    def set(self, field, value):
        field.set(self, value)

    def get(self, field):
        return field.get(self)

    def prettyString(self, sf):
        string = "Age(self: " + self  # TODO
        p = sf.poolByName.get(self.skillName)
        self.printFs(p.allFields(), string)
        string += ")"
        return string

    def printFs(self, fieldIterator, string):
        while fieldIterator.hasNext():
            f = fieldIterator.__next__()
            string += ", " + f.name + ": " + f.get(self)


class SubType(SkillObject, NamedType):

    def __init__(self, tpool: StoragePool, skillID):
        super(SubType, self).__init__(skillID)
        self.tpool: StoragePool = tpool

    def skillName(self):
        return self.tpool.name

    def toString(self):
        return self.skillName() + "#" + self.skillID
