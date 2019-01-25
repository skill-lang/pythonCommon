import abc
import os
import struct
from io import BufferedReader
from pathlib import Path


class InStream(abc.ABC):
    """
    Implementations of this class are used to turn a byte stream into a stream of integers and floats
    """

    def __init__(self, reader: BufferedReader):
        self.file: BufferedReader = reader

    def f64(self):
        return float(struct.unpack('>d', self.file.read(8))[0])

    def f32(self):
        return float(struct.unpack('>f', self.file.read(4))[0])

    def v32(self):
        rval = self.i8()
        if (rval & 0x80) != 0:
            self.multibytev32(rval)
        else:
            return rval

    def multibytev32(self, rval):
        r = self.i8()
        rval = (rval & 0x7f) | ((r & 0x7f) << 7)

        if (r & 0x80) != 0:
            r = self.i8()
            rval = rval | ((r & 0x7f) << 14)
            if (r & 0x80) != 0:
                r = self.i8()
                rval = rval | ((r & 0x7f) << 21)
                if (r & 0x80) != 0:
                    r = self.i8()
                    rval = rval | ((r & 0x7f) << 28)
                    if (r & 0x80) != 0:
                        raise Exception("unexpected overlong v64 value (expected 32bit)")
        return rval

    def v64(self):
        rval = self.i8()
        if (rval & 0x80) != 0:
            self.multibytev64(rval)
        else:
            return rval

    def multibytev64(self, rval):
        r = self.i8()
        rval = (rval & 0x7f) | ((r & 0x7f) << 7)

        if (r & 0x80) != 0:
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
