import abc, struct, os
from typing import BinaryIO
from io import FileIO


class InStream(abc.ABC, BinaryIO):
    """
    Implementations of this class are used to turn a byte stream into a stream of integers and floats
    """

    def __init__(self, file: FileIO):
        self.file = file

    def f64(self):
        return float(struct.unpack('>d', self.file.read(8))[0])

    def f32(self):
        return float(struct.unpack('>f', self.file.read(4))[0])

    def v32(self):
        #TODO
        pass

    def v64(self):
        #TODO
        pass

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
