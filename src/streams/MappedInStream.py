from src.streams.InStream import InStream
from typing import BinaryIO
from copy import deepcopy
from io import BufferedReader


class MappedInStream(InStream):

    def __init__(self, file: BufferedReader):
        super(MappedInStream, self).__init__(file)

    def view(self, begin):
        f = deepcopy(self.file)
        f.seek(self.file.tell() + begin)
        return f

    def asFileObject(self):
        return self.file

    def toString(self):
        return "MappedInStream(" + super.position() + " -> " + super.eof() - super.file.tell() + ", next: " + super.file.read(
            1) + ")"
