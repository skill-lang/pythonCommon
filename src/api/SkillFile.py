import abc


class SkillFile(abc.ABC):

    @abc.abstractmethod
    def contains(self, target): pass

    @abc.abstractmethod
    def delete(self, target): pass

    @abc.abstractmethod
    def allTypes(self): pass

    @abc.abstractmethod
    def changePath(self, path): pass

    @abc.abstractmethod
    def currentPath(self): pass

    @abc.abstractmethod
    def changeMode(self, writeMode): pass

    @abc.abstractmethod
    def loadLazyData(self): pass

    @abc.abstractmethod
    def check(self): pass

    @abc.abstractmethod
    def flush(self): pass

    @abc.abstractmethod
    def close(self): pass
