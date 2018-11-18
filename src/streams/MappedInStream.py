from src.streams import InStream
from io import FileIO
from copy import copy
from src import Exception

class MappedInStream(InStream):

    def __init__(self, file: FileIO):
        super.__init__(file)


    def view(self, begin, end):
        return copy(self.file)

    def asByteBuffer(self):
        return self.file

    def jump(self):
        raise Exception.IllegalStateException("there is no reason to jump in a mapped stream")

    def toString(self):
        #TODO
        return "MappedInStream(0x%X -> 0x%X, next: 0x%X)"
