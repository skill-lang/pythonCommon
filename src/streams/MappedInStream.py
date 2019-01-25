from src.streams.InStream import InStream
from typing import BinaryIO
from copy import deepcopy
from io import BufferedReader
from pathlib import Path


class MappedInStream(InStream):

    def __init__(self, reader: BufferedReader):
        super(MappedInStream, self).__init__(reader)

    def view(self, begin):
        f = deepcopy(self.file)
        f.seek(self.file.tell() + begin)
        return f

    def asFileObject(self):
        return self.file

    def toString(self):
        return "MappedInStream(" + self.position() + " -> " + (self.eof() - self.file.tell()) + ", next: " + self.file.read(1).decode('utf-8') + ")"
