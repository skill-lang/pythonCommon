import os
from common.streams.InStream import InStream
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
    def open(path):
        if not os.path.exists(path):
            open(path, "x").close()
        file: R = open(path, 'rb+', 4096)  # ignore warning. it's working
        return FileInputStream(file, path)

    def jump(self, position):
        self.file.seek(position)

    def push(self, position):
        self.storedPosition = self.file.tell()
        self.file.seek(position)

    def pop(self):
        if self.storedPosition is not None:
            self.file.seek(self.storedPosition)
        else:
            raise IOError("There is no FileInputStream.storedPosition")

    def close(self):
        self.file.close()
