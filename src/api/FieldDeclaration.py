from abc import ABC, abstractmethod


class FieldDeclaration(ABC):

    @abstractmethod
    def get(self, ref): pass

    @abstractmethod
    def set(self, ref, value): pass
