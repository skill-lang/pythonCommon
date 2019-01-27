from src.streams.InStream import InStream
from typing import BinaryIO, TypeVar
from copy import deepcopy
from io import BufferedReader, BufferedRandom

R = TypeVar('R', BufferedReader, BufferedRandom)


class MappedInStream(InStream):

    def __init__(self, reader: R):
        super(MappedInStream, self).__init__(reader)

    def view(self, begin):
        f = deepcopy(self.file)
        f.seek(self.file.tell() + begin)
        return f

    def asFileObject(self):
        return self.file

    def jump(self):
        return Exception  # TODO Exception

    def toString(self):
        return "MappedInStream(" + self.position() + " -> " + (self.eof() - self.file.tell()) + ", next: " + self.file.read(1).decode('utf-8') + ")"
