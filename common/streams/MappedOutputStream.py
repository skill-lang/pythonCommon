from common.streams.OutStream import OutStream
from typing import TypeVar
from io import BufferedWriter, BufferedRandom
from copy import deepcopy
from mmap import mmap

W = TypeVar('W', BufferedWriter, BufferedRandom)


class MappedOutputStream(OutStream):

    def __init__(self, file: mmap):
        super(MappedOutputStream, self).__init__(file)

    @staticmethod
    def open(fileno, begin, length):
        r = MappedOutputStream(mmap(fileno, length))
        r.file.seek(begin)
        return r
    """
    def clone(self, begin):
        #a = deepcopy(self.file)
        a = mmap(self.file.fileno(), self.file.)
        a.seek(begin)
        return MappedOutputStream(a)
    """
