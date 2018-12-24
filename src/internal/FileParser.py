import abc
from src.streams.FileInputStream import FileInputStream
from src.internal.fieldTypes.Annotation import Annotation
from src.internal.StringPool import StringPool
from src.internal.StoragePool import StoragePool
from src.internal.FieldType import FieldType
from typing import List, Mapping
from src.internal.Exceptions import *
from typing import Generic, TypeVar
from src.internal.parts.Block import Block


class DataEntry:

    def __init__(self, owner: StoragePool, fieldID):
        self.owner = owner
        self.fieldID = fieldID


class LFEntry:

    def __init__(self, p: StoragePool, count):
        self.count = count
        self.p = p


class FileParser(abc.ABC):

    def __init__(self, inStream: FileInputStream):
        self.inStream = inStream

        self.types = []
        self.poolByName = dict()
        self.annotation = Annotation(self.types)
        self.strings = StringPool(self.inStream)
        self.blockCounter = 0
        self.seenTypes = set()
        self.blockIDBarrier = 0
        self.fieldDataQueue = []

        while not inStream.eof():
            self.stringBlock()
            self.typeBlock()
            # not end of runtime
            # implementation does things here

    def stringBlock(self):
        try:
            count = self.inStream.v32()

            if count != 0:
                offset = []
                last = 0
                for i in range(0, count):
                    offset.append(self.inStream.i32())
                for j in range(0, count):
                    add = StringPool.Position(self.inStream.position() + last, offset[j] - last)
                    self.strings.stringPositions.append(add)
                    self.strings.idMap.append(None)
                    self.strings.idMap.append(None)
                    last = offset[j]

                self.inStream.jump(self.inStream.position() + last)
        except Exception as e:
            raise ParseException(self.inStream, self.blockCounter, e, "corrupted string block")

    def typeDefinition(self):

        try:
            n = self.strings.get(self.inStream.v32())
            name: str = n
        except InvalidPoolIndexException as e:
            raise ParseException(self.inStream, self.blockCounter, e, "corrupted type header")

        if name is None:
            raise ParseException(self.inStream, self.blockCounter, None, "corrupted file: nullptr in typename")

        if self.seenTypes.__contains__(name):
            raise ParseException(self.inStream, self.blockCounter, None, "Duplicate definition of type {}", name)
        self.seenTypes.add(name)

        # try to parse the type definition
        try:
            count = self.inStream.v32()
            # definition: StoragePool = None
            if name in self.poolByName:
                definition: StoragePool = self.poolByName.get(name)
            else:
                rest = self.typeRestriction()
                superID = self.inStream.v32()
                # superDef: StoragePool = None
                if superID == 0:
                    superDef: StoragePool = None
                elif superID > self.types.__len__():
                    raise ParseException(self.inStream, self.blockCounter, None,
                                         "Type {} refers to an ill-formed super type.\n"
                                         + "          found: {}; current number of other types {}",
                                         name, superID, self.types.__len__())
                else:
                    superDef: StoragePool = self.types[superID - 1]

                try:
                    definition = StoragePool(0, name, superDef, rest, None)  # TODO fill poolIndex and autoFields
                    if definition.superPool is not superDef:
                        if superDef is None:
                            raise ParseException(self.inStream, self.blockCounter, None,
                                                 "The file contains a super type {}"
                                                 "but {} is specified to be a base type.", "<none>", name)
                        else:
                            raise ParseException(self.inStream, self.blockCounter, None,
                                                 "The file contains a super type {}"
                                                 "but {} is specified to be a base type.", superDef.name, name)
                    self.poolByName[name] = definition
                except Exception as ex:
                    raise ParseException(self.inStream, self.blockCounter, ex,
                                         "The super type of {} stored in the file does not match the specification!",
                                         name)
            if self.blockIDBarrier < definition.typeID():
                self.blockIDBarrier = definition.typeID()
            else:
                raise ParseException(self.inStream, self.blockCounter, None,
                                     "Found unordered type block. Type {} has id {}, barrier was {}.", name,
                                     definition.typeID(), self.blockIDBarrier)

            bpo = definition.basePool.cachedSize
            if definition.superPool is not None:
                if count != 0:
                    bpo += self.inStream.v64()
                else:
                    bpo += definition.superPool.lastBlock().bpo

            if definition.superPool is not None:
                b: Block = definition.superPool.lastBlock()
                if bpo < b.bpo or (b.bpo + b.staticCount) < bpo:
                    raise ParseException(self.inStream, self.blockCounter, None, "Found broken bpo.")

            definition.blocks.append(Block(bpo, count, count))
            definition.staticDataInstances += count

            # TODO add new entry to localFields
        except Exception as exc:
            raise ParseException(self.inStream, self.blockCounter, exc, "unexpected end of file")

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

    def typeRestriction(self) -> set:
        pass

    def fieldRestriction(self, t: FieldType) -> set:
        rval = set()

        count = self.inStream.v32()
        for i in range(0, count, -1):
            id = self.inStream.v32()
            if id == 0: pass
            if id == 1: pass
            if id == 3: pass
            if id == 5: pass
            if id == 7: pass
            if id == 9:
                pass
            else:
                pass

        return rval
