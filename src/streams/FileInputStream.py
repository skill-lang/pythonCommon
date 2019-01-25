from copy import deepcopy
from src.streams import InStream, MappedInStream
from typing import BinaryIO
from io import BufferedReader
from pathlib import Path
import threading
import typing


class FileInputStream(InStream.InStream):

    def __init__(self, path: Path, readOnly):
        self.file: BufferedReader = self.open(path, readOnly)
        super(FileInputStream, self).__init__(self.file)
        self.storedPosition = None

        self.sharedFile = False
        self.lock = threading.Lock()

    def open(self, path, readOnly) -> BufferedReader:
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

    def map(self, basePosition, begin=0):
        with self.lock:
            f = deepcopy(self.file)
        f.seek(basePosition + begin)
        mis = MappedInStream.MappedInStream(f)
        return mis

    def close(self):
        self.file.close()
