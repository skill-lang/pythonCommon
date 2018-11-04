from internal import SkillObject

class Age(SkillObject):

    def __init__(self, skillId=-1, age=0):
        super.skillId = skillId
        self.age = age

    def skillName(self):
        return "age"

    def setAge(self, age):
        self.age = age

    def getAge(self):
        return self.age
