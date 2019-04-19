import os
from common.streams.OutStream import OutStream
from typing import TypeVar
from io import BufferedWriter, BufferedRandom

W = TypeVar('W', BufferedWriter, BufferedRandom)


class FileOutputStream(OutStream):

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

    def flush(self):
        if self.file is not None:
            self.file.flush()

    def close(self):
        if not self.file.closed:
            self.flush()
            self.file.truncate(self.file.tell())
            self.file.close()
