from src.internal.StoragePool import StoragePool


class FieldDeclaration:

    def __init__(self):
        self.owner = StoragePool()

    def owner(self) -> StoragePool:
        return self.owner
