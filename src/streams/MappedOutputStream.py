from src.streams.OutStream import OutStream
from typing import BinaryIO, TypeVar
from io import BufferedWriter, BufferedRandom
from copy import deepcopy

W = TypeVar('W', BufferedWriter, BufferedRandom)


class MappedOutputStream(OutStream):

    def __init__(self, file: W):
        super(MappedOutputStream, self).__init__(file)

    def clone(self, begin):
        a = deepcopy(self.file)
        a.seek(begin)
        return MappedOutputStream(a)

    def close(self):
        if not self.file.closed:
            self.file.close()
