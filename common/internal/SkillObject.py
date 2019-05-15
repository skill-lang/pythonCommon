
class SkillObject:
    """
    Superclass for all user types.
    """

    def __init__(self, skillId):
        self.skillID = skillId
        self.skillName = None

    def isDeleted(self):
        """
        Evaluates if this object will be ignored when writing.
        :return: True iff skillID is 0
        """
        return 0 == self.skillID

    def set(self, field, value):
        """
        Set field value.
        :param field: FieldDeclaration
        :param value:
        :return:
        """
        field.set(self, value)

    def get(self, field):
        """
        :param field: FieldDeclaration
        :return: value of field
        """
        return field.get(self)

    def getSkillID(self):
        """
        :return: skillID of this object
        """
        return self.skillID

    def printFields(self, fieldIterator, string=""):
        """
        Prints FieldDeclarations in order provided by the fieldIterator
        :param fieldIterator: FieldIterator
        :param string: beginning of return string
        :return: names and values of FieldDeclarations as string
        """
        while fieldIterator.hasNext():
            f = fieldIterator.__next__()
            string += ", " + f.name() + ": " + f.get(self)
