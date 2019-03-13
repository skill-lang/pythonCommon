
class SkillObject:

    def __init__(self, skillId):
        self.skillID = skillId
        self.skillName = None

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
