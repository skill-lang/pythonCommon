from copy import deepcopy
from common.streams.InStream import InStream
from common.streams.MappedInStream import MappedInStream
from io import BufferedReader, BufferedRandom
import threading
from typing import TypeVar

R = TypeVar('R', BufferedReader, BufferedRandom)


class FileInputStream(InStream):

    lock = threading.Lock()

    def __init__(self, file: R, path):
        super(FileInputStream, self).__init__(file)
        self.path = path
        self.storedPosition = None
        self.pos = 0

    @staticmethod
    def open(path, readOnly):
        if readOnly:
            file: R = open(path, 'rb', 4096)
        else:
            file: R = open(path, 'rb+', 4096)
        return FileInputStream(file, path)

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
