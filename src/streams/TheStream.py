import os
import struct
from typing import BinaryIO
from io import BytesIO


class TheStream:

    def __init__(self, file: BytesIO):
        self.file = file

    def getF64(self):
        return float(struct.unpack('f', self.file.read(8))[0])

    def getF32(self):
        return float(struct.unpack('f', self.file.read(4))[0])

    def getV32(self):
        # TODO
        pass

    def getV64(self):
        # TODO
        pass

    def getI64(self):
        return int(struct.unpack('l', self.file.read(8))[0])

    def getI32(self):
        return int(struct.unpack('i', self.file.read(4))[0])

    def getI16(self):
        return int(struct.unpack('h', self.file.read(2))[0])

    def getI8(self):
        return int(struct.unpack('b', self.file.read(1))[0])

    def getBool(self):
        return struct.unpack('?', self.file.read())

    def getBytes(self, length):
        return self.file.read(length)

    def has(self, n=0):
        """if n=0 then return number of bytes left in the file, else true if at least n bytes left in the file"""
        if n > 0:
            return os.fstat(self.file.fileno()).st_size <= n
        else:
            return os.fstat(self.file.fileno()).st_size

    def eof(self):
        return self.file.tell() == os.fstat(self.file.fileno()).st_size

    def position(self):
        return self.file.tell()

    def refresh(self):
        if self.file is None or self.has() == 0:
            self.file.flush()
            os.fsync(self.file.fileno())

    def SetBool(self, data=False):
        self.refresh()

        if data:
            e = self.file.write(0xFF.to_bytes(1, "big"))
        else:
            e = self.file.write(0x00.to_bytes(1, "big"))

        if e is not 1:
            raise RuntimeError

    def SetI8(self, data):
        self.refresh()
        self.file.write(struct.pack('b', data))

    def SetI16(self, data):
        self.refresh()
        self.file.write(struct.pack('h', data))

    def SetI32(self, data):
        self.refresh()
        self.file.write(struct.pack('i', data))

    def SetI64(self, data):
        self.refresh()
        self.file.write(struct.pack('l', data))

    def SetV64(self, data):
        # TODO
        pass

    def SetF32(self, data):
        self.refresh()
        self.file.write(struct.pack('f', data))

    def SetF64(self, data):
        self.refresh()
        self.file.write(struct.pack('d', data))

    def close(self):
        self.file.close()
