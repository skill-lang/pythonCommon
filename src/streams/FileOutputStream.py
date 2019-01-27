import os
import threading
from copy import deepcopy
from src.streams.OutStream import OutStream
import struct
from typing import *
from src.streams.MappedOutputStream import MappedOutputStream
from src.streams.FileInputStream import FileInputStream
from io import BufferedWriter, BufferedRandom

W = TypeVar('W', BufferedWriter, BufferedRandom)


class FileOutputStream(OutStream):

    lock = threading.Lock()

    def __init__(self, file: W, position=0):
        super(FileOutputStream, self).__init__(file)
        self.pos = position


    @staticmethod
    def write(target: FileInputStream):
        f: W = target.file
        if f.closed:
            f = open(target.path, 'wb+')
        f.seek(0)
        return FileOutputStream(f)

    @staticmethod
    def append(target: FileInputStream):
        f: W = target.file
        if f.closed:
            f = open(target.path, 'rb+')
        size = os.stat(target.path).st_size
        f.seek(size)
        return FileOutputStream(f, size)

    def put(self, data):
        self.refresh()
        self.file.write(struct.pack('>s', data))

    def mapBlock(self, size) -> MappedOutputStream:
        with self.lock:
            r = deepcopy(self.file)
        self.pos += size
        return MappedOutputStream(r)

    def close(self):
        if not self.file.closed:
            self.file.close()
