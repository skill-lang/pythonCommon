from abc import ABC, abstractmethod
from src.api.SkillFile import SkillFile


class GeneralAccess(ABC):

    def __iter__(self): pass

    name: str

    @abstractmethod
    def size(self): pass


class Access(ABC, GeneralAccess):

    owner: SkillFile

    @abstractmethod
    def stream(self): pass

    @abstractmethod
    def typeOrderIterator(self): pass

    @abstractmethod
    def staticInstances(self): pass

    @abstractmethod
    def superName(self): pass

    @abstractmethod
    def fields(self): pass

    @abstractmethod
    def allFields(self): pass

    @abstractmethod
    def make(self): pass


class StringAccess(ABC):

    @abstractmethod
    def get(self) -> str: pass
