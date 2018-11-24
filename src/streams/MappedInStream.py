from src.streams import InStream
from io import FileIO
from copy import deepcopy


class MappedInStream(InStream):

    def __init__(self, file: FileIO):
        super.__init__(file)

    def view(self, begin):
        f = deepcopy(self.file)
        f.seek(self.file.tell() + begin)
        return f

    def asFileObject(self):
        return self.file

    def toString(self):
        return "MappedInStream(" + super.position() + " -> " + super.eof() - super.file.tell() + ", next: " + super.file.read(
            1) + ")"
