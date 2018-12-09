from src.streams.OutStream import OutStream
from typing import Union, BinaryIO
from src.streams.MappedOutputStream import MappedOutputStream
from io import BufferedWriter


class FileOutputStream(OutStream):

    def __init__(self, file: BufferedWriter):
        super(FileOutputStream, self).__init__(file)

    def write(self, b: Union[bytes, bytearray]):
        # TODO maybe restrictions, method is useless otherwise
        self.file.write(b)

    def mapBlock(self) -> MappedOutputStream:
        pass
