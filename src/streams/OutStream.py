import abc
import os
from io import FileIO


class OutStream(abc.ABC):

    def __init__(self, buffer: FileIO):
        self.buffer = buffer
        self.position = 0

    def position(self):
        if self.buffer is None:
            return self.position
        else:
            return self.buffer.tell() + self.position

    def refresh(self):
        self.buffer.flush()
        os.fsync()

    def bool(self, data):
        pass

    def i8(self, data):
        pass

    def i16(self, data):
        pass

    def i32(self, data):
        pass

    def i64(self, data):
        pass

    @abc.abstractmethod
    def v64(self, data):
        pass

    def f32(self, data):
        pass

    def f64(self, data):
        pass
