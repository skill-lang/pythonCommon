import abc
import os
import struct
from typing import BinaryIO
from io import BufferedWriter


class OutStream(abc.ABC):

    def __init__(self, file: BufferedWriter):
        self.file = file

    def position(self):
        return self.file.tell()

    def refresh(self):
        if self.file is None or self.has() == 0:
            self.file.flush()
            os.fsync(self.file.fileno())

    def bool(self, data=False):
        self.refresh()

        if data:
            e = self.file.write(0xFF.to_bytes(1, "big"))
        else:
            e = self.file.write(0x00.to_bytes(1, "big"))

        if e is not 1:
            raise RuntimeError

    def i8(self, data):
        self.refresh()
        self.file.write(struct.pack('>b', data))

    def i16(self, data):
        self.refresh()
        self.file.write(struct.pack('>h', data))

    def i32(self, data):
        self.refresh()
        self.file.write(struct.pack('>i', data))

    def i64(self, data):
        self.refresh()
        self.file.write(struct.pack('>q', data))

    def v64(self, data):
        # TODO
        pass

    def f32(self, data):
        self.refresh()
        self.file.write(struct.pack('>f', data))

    def f64(self, data):
        self.refresh()
        self.file.write(struct.pack('>d', data))

    def has(self, n=0):
        """if n=0 then return number of bytes left in the file, else true if at least n bytes left in the file"""
        if n > 0:
            return os.fstat(self.file.fileno()).st_size <= n
        else:
            return os.fstat(self.file.fileno()).st_size
