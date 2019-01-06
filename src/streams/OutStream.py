import abc
import os
import struct
import copy
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

    def v64(self, data: int):
        if self.file is None:
            self.refresh()

        size = 0
        a = copy.deepcopy(data)
        while a:
            a = a >> 7
            size += 1

        if not size:
            result = [0]
            return result
        elif size == 10:
            size = 9

        count = 0
        result = []
        while count < 8 and count < (size - 1):
            result[count] = a >> (7*count)
            result[count] |= 0x80
            count += 1
        result[count] = a >> (7 * count)
        return result

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
