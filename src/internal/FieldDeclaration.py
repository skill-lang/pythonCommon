from src.internal.StoragePool import StoragePool
from src.internal.FieldRestriction import FieldRestriction


class FieldDeclaration:

    def __init__(self):
        self.owner = StoragePool()

    def owner(self) -> StoragePool:
        return self.owner

    def addRestriction(self, r: FieldRestriction):
        pass

    def addChunk(self, chunk):
        pass
