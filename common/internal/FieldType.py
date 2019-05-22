from typing import Union


class FieldType:
    """
    Superclass of all possible types of a field
    """

    def __init__(self, typeID):
        self._typeID = typeID

    def typeID(self):
        return self._typeID

    def __eq__(self, obj):
        """
        Is executed if two objects are compared with '=='
        :param obj: object to compare with
        :return: True iff obj and self have same typeID, else False
        """
        if isinstance(obj, FieldType):
            return obj.typeID() == self.typeID()
        return False

    def __hash__(self): return self.typeID()

    def readSingleField(self, inStream):
        """
        Reads one instance of this field type
        :param inStream: FileInputStream
        :return: instance of this field type
        """
        pass

    def calculateOffset(self, xs: Union[list, dict, set]):
        """
        Calculates offset of all instances in xs
        :param xs: collection of instances
        :return: offset
        """
        pass

    def singleOffset(self, x):
        """
        Calculates offset of x
        :param x: instance of this field type
        :return: offset of x
        """
        pass

    def writeSingleField(self, data, out):
        """
        Writes instance data of this field type to the file
        :param data: instance of this field type
        :param out: FileOutputStream
        :return:
        """
        pass

    def __str__(self):
        """
        Field type as a string
        :return: string
        """
        pass
