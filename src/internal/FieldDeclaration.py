from src.internal.StoragePool import StoragePool
from src.internal.FieldRestriction import FieldRestriction
from src.internal.SkillObject import SkillObject
from src.internal.FieldType import FieldType
from src.internal.parts.Blocks import *


class FieldDeclaration(dict):

    def __init__(self, type: FieldType, name, owner: StoragePool, index=-1):
        super(FieldDeclaration, self).__init__()
        self.type = type
        self.name = name

        self.owner: StoragePool = owner
        self.owner.dataFields.append(self)
        if index == -1:
            self.index = len(self.owner.dataFields)
        else:
            self.owner.autoFields[-index] = self

        self.restrictions = set()
        self.dataChunks = []

    def addRestriction(self, r: FieldRestriction):
        self.restrictions.add(r)

    def check(self):
        if len(self.restrictions) != 0:
            for x in self.owner:
                if not x.isDeleted():
                    for r in self.restrictions:
                        r.check(self.get(x))

    def toString(self):
        return self.type.toString() + " " + self.name

    def equals(self, obj):
        if self == obj:
            return True
        if isinstance(obj, FieldDeclaration):
            return obj.name == self.name and obj.type == self.type
        return False

    def addChunk(self, chunk):
        self.dataChunks.append(chunk)

    def addOffsetToLastChunk(self, offset):
        c = self.lastChunk()
        c.begin += offset
        c.end += offset
        return c.end

    def lastChunk(self):
        return self.dataChunks[len(self.dataChunks) - 1]

    def resetChunks(self, lbpo, newSize):
        self.dataChunks.clear()
        self.dataChunks.append(SimpleChunk(-1, -1, lbpo, newSize))


class KnownField(dict):
    pass
