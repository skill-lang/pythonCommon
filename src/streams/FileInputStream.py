from src.streams import InStream
from io import FileIO


class FileInputStream(InStream):

    def __init__(self, path):
        super(FileInputStream, self).__init__(file)

    def open(self, path, readOnly):
        return self.__init__()

    def jump(self, position):
        self.file.seek(position)
        pass

    def jumpAndMap(self, offset):
        pass

    def push(self, position):
        self.storedPosition = self.file.tell()
        self.file.seek(position)