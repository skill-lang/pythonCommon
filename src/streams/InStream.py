import abc, struct, os
from io import FileIO


class InStream(abc.ABC):
    """
    Implementations of this class are used to turn a byte stream into a stream of integers and floats
    """

    def __init__(self, file: FileIO):
        self.file = file

    def f64(self):
        return float(struct.unpack('f', self.file.read(8)))

    def f32(self):
        return float(struct.unpack('f', self.file.read(4)))

    def v32(self):
        #TODO
        pass

    def i64(self):
        return int(struct.unpack('l', self.file.read(8)))

    def i32(self):
        return int(struct.unpack('i', self.file.read(4)))

    def i16(self):
        return int(struct.unpack('h', self.file.read(2)))

    def i8(self):
        return int(struct.unpack('b', self.file.read(1)))

    def bool(self):
        return struct.unpack('?', self.file.read())

    def bytes(self, length):
        return bytearray.fromhex(self.file.read(length))

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
