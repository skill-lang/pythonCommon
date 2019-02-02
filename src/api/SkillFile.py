import abc
import logging
import enum

logger = logging.getLogger()


class ActualMode:

    def __init__(self, *modes):
        self.openMode = None
        self.closeMode = None
        for m in modes:
            if m == SkillFile.Mode.Read or m == SkillFile.Mode.Create:
                if self.openMode is None:
                    self.openMode = m
                elif self.openMode != m:
                    raise IOError(logger.error("You can either create or read a file."))
            elif m == SkillFile.Mode.Write or m == SkillFile.Mode.Append:
                if self.closeMode is None:
                    self.closeMode = m
                elif self.closeMode != m:
                    raise IOError(logger.error("You can either write or append to a file."))
            elif m == SkillFile.Mode.ReadOnly:
                if self.closeMode is None:
                    self.closeMode = m
                elif self.closeMode != m:
                    raise IOError(logger.error("You cannot combine ReadOnly with another write mode."))
        if self.openMode is None: self.openMode = "Read"
        if self.closeMode is None: self.closeMode = "Write"


class SkillFile(abc.ABC):

    class Mode(enum):
        Create = 0
        Read = 1
        Write = 2
        Append = 3
        ReadOnly = 4

    @abc.abstractmethod
    def Strings(self): pass

    @abc.abstractmethod
    def contains(self, target): pass

    @abc.abstractmethod
    def delete(self, target): pass

    @abc.abstractmethod
    def allTypes(self): pass

    @abc.abstractmethod
    def allTypesStream(self): pass

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
