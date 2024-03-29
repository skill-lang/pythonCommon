from enum import Enum


class Mode(Enum):
    """
    Read and write modes
    """
    Create = 0
    Read = 1
    Write = 2
    Append = 3
    ReadOnly = 4


class ActualMode:

    def __init__(self, modes):
        """
        Calculate read and write mode
        :param modes: list of modes
        """
        self.openMode = None
        self.closeMode = None
        for m in modes:
            if m == Mode.Read or m == Mode.Create:
                if self.openMode is None:
                    self.openMode = m
                elif self.openMode != m:
                    raise IOError("You can either create or read a file.")
            elif m == Mode.Write or m == Mode.Append:
                if self.closeMode is None:
                    self.closeMode = m
                elif self.closeMode != m:
                    raise IOError("You can either write or append to a file.")
            elif m == Mode.ReadOnly:
                if self.closeMode is None:
                    self.closeMode = m
                elif self.closeMode != m:
                    raise IOError("You cannot combine ReadOnly with another write mode.")
        if self.openMode is None:
            self.openMode = Mode.Read
        if self.closeMode is None:
            self.closeMode = Mode.Write
