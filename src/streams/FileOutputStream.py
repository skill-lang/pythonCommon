from src.streams.OutStream import OutStream
import struct
from typing import Union, BinaryIO
from src.streams.MappedOutputStream import MappedOutputStream
from src.streams.FileInputStream import FileInputStream
from io import BufferedWriter


class FileOutputStream(OutStream):

    def __init__(self, file: BufferedWriter):
        super(FileOutputStream, self).__init__(file)

    @staticmethod
    def write(target: FileInputStream):
        f = target.file
        if f.closed:
            f = open(target.path, 'wb+')
        f.seek(0)
        return FileOutputStream(f)

    def put(self, data):
        self.file.write(struct.pack('>s', data))

    def mapBlock(self) -> MappedOutputStream:
        pass

    def close(self):
        self.file.close()
