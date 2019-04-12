import abc
import os
import struct
import copy
from io import BufferedWriter


class OutStream(abc.ABC):

    def __init__(self, file):
        self.file: BufferedWriter = file
        self.pos = 0

    def position(self):
        if self.file is None:
            return self.pos
        else:
            return self.file.tell() + self.pos

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
        # self.file.write(data.to_bytes(1, "big"))
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

    @staticmethod
    def __toByte(data):
        return data & 0xFF

    def __writeByte(self, data):
        self.file.write(struct.pack('>B', data))

    def v64(self, data: int):
        if self.file is None:
            self.refresh()
        v = data
        if 0 == (v & 0xFFFFFFFFFFFFFF80):
            self.__writeByte(self.__toByte(v))
        else:
            self.__writeByte(0x80 | self.__toByte(v))
            if 0 == (v & 0xFFFFFFFFFFFFC000):
                self.__writeByte(self.__toByte(v >> 7))
            else:
                self.__writeByte(0x80 | self.__toByte(v >> 7))
                if 0 == (v & 0xFFFFFFFFFFE00000):
                    self.__writeByte(self.__toByte(v >> 14))
                else:
                    self.__writeByte(0x80 | self.__toByte(v >> 14))
                    if 0 == (v & 0xFFFFFFFFF0000000):
                        self.__writeByte(self.__toByte(v >> 21))
                    else:
                        self.__writeByte(0x80 | self.__toByte(v >> 21))
                        if 0 == (v & 0xFFFFFFF800000000):
                            self.__writeByte(self.__toByte(v >> 28))
                        else:
                            self.__writeByte(0x80 | self.__toByte(v >> 28))
                            if 0 == (v & 0xFFFFFC0000000000):
                                self.__writeByte(self.__toByte(v >> 35))
                            else:
                                self.__writeByte(0x80 | self.__toByte(v >> 35))
                                if 0 == (v & 0xFFFE000000000000):
                                    self.__writeByte(self.__toByte(v >> 42))
                                else:
                                    self.__writeByte(0x80 | self.__toByte(v >> 42))
                                    if 0 == (v & 0xFF00000000000000):
                                        self.__writeByte(self.__toByte(v >> 49))
                                    else:
                                        self.__writeByte(0x80 | self.__toByte(v >> 49))
                                        self.__writeByte(self.__toByte(v >> 56))

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

    def put(self, data):
        self.refresh()
        self.file.write(data)
        self.pos += len(data)
