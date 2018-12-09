from src.streams.OutStream import OutStream
from typing import BinaryIO
from io import BufferedWriter


class MappedOutputStream(OutStream):

    def __init__(self, file: BufferedWriter):
        super(MappedOutputStream, self).__init__(file)
