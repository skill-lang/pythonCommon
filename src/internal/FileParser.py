import abc
from src.streams.FileInputStream import FileInputStream
from src.internal.StringPool import StringPool
from src.internal.fieldTypes.Annotation import Annotation
from src.internal.StoragePool import StoragePool
from typing import List, Mapping


class FileParser(abc.ABC):

    types = List[StoragePool]
    poolByName = Mapping[str, StoragePool]
    annotation = Annotation()

    def __init__(self, inStream: FileInputStream):
        self.inStream = inStream

        while not inStream.eof():
            self.stringBlock()
            self.typeBlock()
            # not end of runtime
            # implementation does things here

    def stringBlock(self):
        count = self.inStream.v32()

        if count != 0:
            offset = []
            last = 0
            for i in range(0, count):
                offset.append(self.inStream.i32())
                # TODO add stringPositions to StringPool
                last = offset[i]

            self.inStream.jump(self.inStream.position() + last)

    def typeDefinition(self):
        pass

    def typeBlock(self):

        # parse type
        count = self.inStream.v32()
        for i in range(0, count, -1):
            self.typeDefinition()

        # resize pools by updating cachedSize and staticCount

        # parse fields

        self.processFieldData()

    def processFieldData(self):
        pass
