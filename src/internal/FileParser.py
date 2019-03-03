from src.internal.fieldTypes.Annotation import Annotation
from src.internal.fieldTypes.BoolType import BoolType
from src.internal.fieldTypes.ConstantLengthArray import ConstantLengthArray
from src.internal.fieldTypes.ConstantTypes import ConstantI8
from src.internal.fieldTypes.ConstantTypes import ConstantI16
from src.internal.fieldTypes.ConstantTypes import ConstantI32
from src.internal.fieldTypes.ConstantTypes import ConstantI64
from src.internal.fieldTypes.ConstantTypes import ConstantV64
from src.internal.fieldTypes.FloatType import F32
from src.internal.fieldTypes.FloatType import F64
from src.internal.fieldTypes.IntegerTypes import I8
from src.internal.fieldTypes.IntegerTypes import I16
from src.internal.fieldTypes.IntegerTypes import I32
from src.internal.fieldTypes.IntegerTypes import I64
from src.internal.fieldTypes.IntegerTypes import V64
from src.internal.fieldTypes.ListType import ListType
from src.internal.fieldTypes.MapType import MapType
from src.internal.fieldTypes.SetType import SetType
from src.internal.fieldTypes.VariableLengthArray import VariableLengthArray
from src.internal.StringPool import StringPool
from src.internal.StoragePool import StoragePool
from src.internal.Exceptions import SkillException, ParseException, InvalidPoolIndexException
from src.internal.Blocks import Block, SimpleChunk, BulkChunk
from src.internal.FieldDeclaration import FieldDeclaration
from src.streams.FileInputStream import FileInputStream


class DataEntry:

    def __init__(self, owner: StoragePool, fieldID):
        self.owner = owner
        self.fieldID = fieldID


class LFEntry:

    def __init__(self, p: StoragePool, count):
        self.count = count
        self.p = p


class FileParser:

    localFields = []

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
        self.offset = 0

        while not inStream.eof():
            self.stringBlock()
            self.typeBlock()
            # not end of runtime
            # implementation does things here

    @staticmethod
    def newPool(name: str, superPool: StoragePool, types: []):
        pass

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
                    last = offset[j]

                self.inStream.jump(self.inStream.position() + last)
        except Exception as e:
            raise ParseException(self.inStream, self.blockCounter, e, "corrupted string block")

    def typeDefinition(self):

        try:
            n = self.strings.get(self.inStream.v32())
            name: str = n
        except InvalidPoolIndexException as e:
            raise ParseException(self.inStream, self.blockCounter, e, "corrupted fType header")

        if name is None:
            raise ParseException(self.inStream, self.blockCounter, None, "corrupted file: nullptr in typename")

        if self.seenTypes.__contains__(name):
            raise ParseException(self.inStream, self.blockCounter, None, "Duplicate definition of fType {}", name)
        self.seenTypes.add(name)

        # try to parse the fType definition
        try:
            count = self.inStream.v32()
            # definition: StoragePool = None
            if name in self.poolByName:
                definition: StoragePool = self.poolByName.get(name)
            else:
                superID = self.inStream.v32()
                # superDef: StoragePool = None
                if superID == 0:
                    superDef: StoragePool = None
                elif superID > self.types.__len__():
                    raise ParseException(self.inStream, self.blockCounter, None,
                                         "Type {} refers to an ill-formed super fType.\n"
                                         + "          found: {}; current number of other types {}",
                                         name, superID, self.types.__len__())
                else:
                    superDef: StoragePool = self.types[superID - 1]

                try:
                    definition = self.newPool(name, superDef, self.types)
                    if definition.superPool is not superDef:
                        if superDef is None:
                            raise ParseException(self.inStream, self.blockCounter, None,
                                                 "The file contains a super fType {}"
                                                 "but {} is specified to be a base fType.", "<none>", name)
                        else:
                            raise ParseException(self.inStream, self.blockCounter, None,
                                                 "The file contains a super fType {}"
                                                 "but {} is specified to be a base fType.", superDef.__name__, name)
                    self.poolByName[name] = definition
                except Exception as ex:
                    raise ParseException(self.inStream, self.blockCounter, ex,
                                         "The super fType of {} stored in the file does not match the specification!",
                                         name)
            if self.blockIDBarrier < definition.typeID():
                self.blockIDBarrier = definition.typeID()
            else:
                raise ParseException(self.inStream, self.blockCounter, None,
                                     "Found unordered fType block. Type {} has id {}, barrier was {}.", name,
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

            self.localFields.append(LFEntry(definition, self.inStream.v64()))
        except Exception as exc:
            raise ParseException(self.inStream, self.blockCounter, exc, "unexpected end of file")

    def typeBlock(self):

        # parse fType
        count = self.inStream.v32()
        for i in range(0, count, -1):
            self.typeDefinition()

        # resize pools by updating cachedSize and staticCount
        for e in self.localFields:
            p: StoragePool = e.p
            b: Block = p.lastBlock()
            p.cachedSize += b.count

            if b.count != 0:
                parent: StoragePool = p.superPool
                if parent is None:
                    sb: Block = parent.lastBlock()
                    delta = sb.staticCount - (b.bpo - sb.bpo)
                    if delta > 0:
                        sb.staticCount -= delta
                        parent.staticDataInstances -= delta

        # parse fields
        for lfe in self.localFields:
            p: StoragePool = lfe.p
            legalFieldIDBarrier = 1 + len(p.dataFields)
            lastBlock: Block = p.blocks.get(len(p.blocks) - 1)
            for fieldcounter in range(lfe.count, 0, -1):
                ID = self.inStream.v32()
                if ID > legalFieldIDBarrier or ID <= 0:
                    raise ParseException(self.inStream, self.blockCounter, None, "Found an illegal field ID: []", ID)
                if ID == legalFieldIDBarrier:
                    fieldName = self.strings.get(self.inStream.v32())
                    if fieldName is None:
                        raise ParseException(self.inStream, self.blockCounter, None,
                                             "corrupted file: nullptr in field name")
                    t = self.fieldType()
                    end = self.inStream.v64()
                    try:
                        f: FieldDeclaration = p.addField(t, fieldName)
                        if len(p.blocks) == 1:
                            f.addChunk(SimpleChunk(self.offset, end, lastBlock.bpo, lastBlock.count))
                        else:
                            f.addChunk(BulkChunk(self.offset, end, p.cachedSize, len(p.blocks)))
                    except SkillException as e:
                        raise ParseException(self.inStream, self.blockCounter, None, e.message)
                    legalFieldIDBarrier += 1
                else:
                    end = self.inStream.v64()
                    p.dataFields[ID - 1].addChunk(SimpleChunk(self.offset, end, lastBlock.bpo, lastBlock.count))

                self.offset = end
                self.fieldDataQueue.append(DataEntry(p, ID))
        self.processFieldData()

    def processFieldData(self):
        fileOffset = self.inStream.position()
        dataEnd = fileOffset
        for e in self.fieldDataQueue:
            f = e.owner.dataFields.get(e.fieldID - 1)
            end = f.addOffsetToLastChunk(self.inStream, fileOffset)
            dataEnd = max(dataEnd, end)
        self.inStream.jump(dataEnd)

    def fieldType(self):
        typeID = self.inStream.v32()
        if typeID == 0:
            return ConstantI8(self.inStream.i8())
        elif typeID == 1:
            return ConstantI16(self.inStream.i16())
        elif typeID == 2:
            return ConstantI32(self.inStream.i32())
        elif typeID == 3:
            return ConstantI64(self.inStream.i64())
        elif typeID == 4:
            return ConstantV64(self.inStream.v64())
        elif typeID == 5:
            return self.annotation
        elif typeID == 6:
            return BoolType()
        elif typeID == 7:
            return I8()
        elif typeID == 8:
            return I16()
        elif typeID == 9:
            return I32()
        elif typeID == 10:
            return I64()
        elif typeID == 11:
            return V64()
        elif typeID == 12:
            return F32()
        elif typeID == 13:
            return F64()
        elif typeID == 14:
            return self.strings
        elif typeID == 15:
            return ConstantLengthArray(self.inStream.v32(), self.fieldType())
        elif typeID == 17:
            return VariableLengthArray(self.fieldType())
        elif typeID == 18:
            return ListType(self.fieldType())
        elif typeID == 19:
            return SetType(self.fieldType())
        elif typeID == 20:
            return MapType(self.fieldType(), self.fieldType())
        elif typeID >= 32:
            return self.types[typeID - 32]
        else:
            raise ParseException(self.inStream, self.blockCounter, None, "Invalid type ID: []", typeID)

    def read(self, cls, writeMode):
        try:
            r = cls(self.poolByName, self.strings, self.annotation, self.types, self.inStream, writeMode)
            r.check()
            return r
        except SkillException as e:
            raise ParseException(self.inStream, self.blockCounter, e, "Post serialization check failed!")
        except Exception as e:
            raise ParseException(self.inStream, self.blockCounter, e, "State instantiation failed!")
