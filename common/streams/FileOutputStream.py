import os
import threading
from copy import deepcopy
from common.streams.OutStream import OutStream
import struct
from typing import TypeVar
from common.streams.MappedOutputStream import MappedOutputStream
from io import BufferedWriter, BufferedRandom

W = TypeVar('W', BufferedWriter, BufferedRandom)


class FileOutputStream(OutStream):

    lock = threading.Lock()

    def __init__(self, file: W, position=0):
        super(FileOutputStream, self).__init__(file)
        self.pos = position

    @staticmethod
    def write(target):
        f: W = target.file
        if f.closed:
            f = open(target.path, 'rb+')
        f.seek(0)
        return FileOutputStream(f)

    @staticmethod
    def append(target):
        f: W = target.file
        if f.closed:
            f = open(target.path, 'rb+')
            return FileOutputStream(f)
        else:
            size = os.stat(target.path).st_size
            f.seek(size)
            return FileOutputStream(f, size)

    def mapBlock(self, size) -> MappedOutputStream:
        fileno = self.file.fileno()
        pos = self.position()
        if self.file is not None:
            self.flush()
            self.close()
        r = MappedOutputStream.open(fileno, pos, size)
        self.pos += size
        return r

    def flush(self):
        if self.file is not None:
            p = self.file.tell()
            self.file.seek(0)
            self.file.flush()
            self.pos += p

    def close(self):
        if not self.file.closed:
            self.flush()
            self.file.close()
            if os.stat(self.file.__sizeof__()).st_size != self.pos:
                self.file.truncate(self.pos)

