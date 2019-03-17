import abc
import os
import struct
from io import BufferedReader, BufferedRandom
from typing import TypeVar

R = TypeVar('R', BufferedReader, BufferedRandom)


class InStream(abc.ABC):
    """
    Implementations of this class are used to turn a byte stream into a stream of integers and floats
    """

    def __init__(self, reader: R):
        self.file: BufferedReader = reader

    def f64(self):
        return float(struct.unpack('>d', self.file.read(8))[0])

    def f32(self):
        return float(struct.unpack('>f', self.file.read(4))[0])

    def v64(self):
        a = []
        result = ''
        for i in range(0, 9):
            b = bin(int(self.file.read(1).hex(), 16))[2:].zfill(8)
            a.append(b)
            if b.startswith('0'):
                break
        for j in range(0, len(a)):
            if j != 8:
                result = result + a[j][1:]
            else:
                result = result + a[j]
        result = int(result, 2)
        return result

    def multiByteV64(self, rval):
        r = self.i8()
        rval = rval | ((r & 0x7f) << 7)
        if (rval & 0x80) != 0:
            r = self.i8()
            rval = rval | ((r & 0x7f) << 14)
            if (r & 0x80) != 0:
                r = self.i8()
                rval = rval | ((r & 0x7f) << 21)
                if (r & 0x80) != 0:
                    r = self.i8()
                    rval = rval | ((r & 0x7f) << 28)
                    if (r & 0x80) != 0:
                        r = self.i8()
                        rval = rval | ((r & 0x7f) << 35)
                        if (r & 0x80) != 0:
                            r = self.i8()
                            rval = rval | ((r & 0x7f) << 42)
                            if (r & 0x80) != 0:
                                r = self.i8()
                                rval = rval | ((r & 0x7f) << 49)
                                if (r & 0x80) != 0:
                                    rval = rval | self.i8() << 56
        return rval

    def i64(self):
        return struct.unpack('>q', self.file.read(8))[0]

    def i32(self):
        return struct.unpack('>i', self.file.read(4))[0]

    def i16(self):
        return struct.unpack('>h', self.file.read(2))[0]

    def i8(self):
        # print("buffer: ", type(self.file), self.file.read(1))
        return struct.unpack('>b', self.file.read(1))[0]

    def bool(self):
        return struct.unpack('?', self.file.read(1))[0]

    def bytes(self, length):
        return self.file.read(length)

    def has(self, n=0):
        """if n=0 then return number of bytes left in the file, else true if at least n bytes left in the file"""
        if n > 0:
            return os.fstat(self.file.fileno()).st_size - self.position() <= n
        else:
            return os.fstat(self.file.fileno()).st_size - self.position()

    def eof(self):
        return self.file.tell() == os.fstat(self.file.fileno()).st_size

    def position(self):
        return self.file.tell()
