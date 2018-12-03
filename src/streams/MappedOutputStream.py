from src.streams import OutStream
from typing import BinaryIO


class MappedOutputStream(OutStream.OutStream):

    def __init__(self, file: BinaryIO):
        super(MappedOutputStream, self).__init__(file)
