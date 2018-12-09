from copy import deepcopy

from src.streams import InStream, MappedInStream
from typing import BinaryIO
from io import BufferedReader


class FileInputStream(InStream.InStream):

    def __init__(self, file: BufferedReader):
        super(FileInputStream, self).__init__(file)
        self.storedPosition = None
        self.path = None

    def open(self, path, readOnly):
        self.path = path
        if readOnly:
            return open(path, 'rb')
        else:
            return open(path, 'rb+')

    def jump(self, position):
        self.file.seek(position)

    def jumpAndMap(self, offset):
        m = self.map()
        self.jump(offset)
        return m

    def push(self, position):
        self.storedPosition = self.file.tell()
        self.file.seek(position)

    def pop(self):
        if self.storedPosition is not None:
            self.file.seek(self.storedPosition)
        else:
            raise IOError("There is no FileInputStream.storedPosition")

    def map(self, begin=0):
        with self.file.lock():
            f = deepcopy(self.file)
        f.seek(self.file.tell() + begin)
        mis = MappedInStream.MappedInStream(f)
        return mis

    def close(self):
        self.file.close()
