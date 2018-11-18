import abc
import logging

logger = logging.getLogger()


def checkActualMode(*modes):
    openMode = None
    closeMode = None
    for m in modes:
        if m == "Create":
            logger.debug("Tried to Create (ActualMode)")
        elif m == "Read":
            if openMode is None:
                openMode = m
            elif openMode != m:
                raise IOError(logger.error("You can either create or read a file."))
        elif m == "Append":
            logger.debug("Tried to Append (ActualMode)")
        elif m == "Write":
            if closeMode is None:
                closeMode = m
            elif closeMode != m:
                raise IOError(logger.error("You can either write or append to a file."))
        elif m == "ReadOnly":
            if closeMode is None:
                closeMode = m
            elif closeMode != m:
                raise IOError(logger.error("You cannot combine ReadOnly with another write mode."))
    if openMode is None: openMode = "Read"
    if closeMode is None: closeMode = "Write"

    return openMode, closeMode


class SkillFile(abc.ABC):
    Mode = ("Create", "Read", "Write", "Append", "ReadOnly")

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
    def curreentPath(self): pass

    @abc.abstractmethod
    def changeMode(self, writemode): pass

    @abc.abstractmethod
    def loadLazyData(self): pass

    @abc.abstractmethod
    def check(self): pass

    @abc.abstractmethod
    def flush(self): pass

    @abc.abstractmethod
    def close(self): pass
