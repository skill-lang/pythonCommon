from copy import deepcopy
from src.streams.InStream import InStream
from src.streams.MappedInStream import MappedInStream
from typing import BinaryIO
from io import BufferedReader, BufferedRandom
from pathlib import Path
import threading
from typing import *
from os import PathLike

R = TypeVar('R', BufferedReader, BufferedRandom)


class FileInputStream(InStream):

    lock = threading.Lock()

    def __init__(self, file: R, path, readOnly):
        super(FileInputStream, self).__init__(file)
        self.path = path
        self.storedPosition = None
        self.sharedFile = not readOnly

    @staticmethod
    def open(path, readOnly):
        if readOnly:
            file: R = open(path, 'rb')
        else:
            file: R = open(path, 'rb+')
        return FileInputStream(file, path, readOnly)

    def shareFile(self):
        self.sharedFile = True
        return self.file

    def jump(self, position):
        self.file.seek(position)

    def jumpAndMap(self, offset):
        m = self.map(self.position())
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

    def map(self, basePosition, begin=0):
        with self.lock:
            f = deepcopy(self.file)
        f.seek(basePosition + begin)
        return MappedInStream(f)

    def close(self):
        self.file.close()
