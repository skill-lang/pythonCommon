from common.internal.fieldTypes.Annotation import Annotation
from common.internal.fieldTypes.BoolType import BoolType
from common.internal.fieldTypes.ConstantLengthArray import ConstantLengthArray
from common.internal.fieldTypes.ConstantTypes import ConstantI8
from common.internal.fieldTypes.ConstantTypes import ConstantI16
from common.internal.fieldTypes.ConstantTypes import ConstantI32
from common.internal.fieldTypes.ConstantTypes import ConstantI64
from common.internal.fieldTypes.ConstantTypes import ConstantV64
from common.internal.fieldTypes.FloatType import F32
from common.internal.fieldTypes.FloatType import F64
from common.internal.fieldTypes.IntegerTypes import I8
from common.internal.fieldTypes.IntegerTypes import I16
from common.internal.fieldTypes.IntegerTypes import I32
from common.internal.fieldTypes.IntegerTypes import I64
from common.internal.fieldTypes.IntegerTypes import V64
from common.internal.fieldTypes.ListType import ListType
from common.internal.fieldTypes.MapType import MapType
from common.internal.fieldTypes.SetType import SetType
from common.internal.fieldTypes.VariableLengthArray import VariableLengthArray
from common.internal.StringPool import StringPool
from common.internal.StoragePool import StoragePool
from common.internal.Exceptions import SkillException, ParseException, InvalidPoolIndexException
from common.internal.Blocks import Block, SimpleChunk, BulkChunk
from common.internal.FieldDeclaration import FieldDeclaration
from common.streams.FileInputStream import FileInputStream
from common.internal.NamedType import NamedType
from common.internal.SkillObject import SkillObject


class DataEntry:

    def __init__(self, owner: StoragePool, fieldID):
        self.owner = owner
        self.fieldID = fieldID


class LFEntry:

    def __init__(self, p: StoragePool, count):
        self.count = count
        self.p = p


class FileParser:

    def __init__(self, inStream: FileInputStream, knownTypes):
        self.blockCounter = 0
        self.seenTypes = set()
        self.blockIDBarrier = 0
        self.poolByName = dict()
        self.localFields = []
        self.fieldDataQueue = []
        self.offset = 0
        self.types = []
        self.inStream = inStream
        self.strings = StringPool(self.inStream)
        self.annotation = Annotation(self.types)

        self.knownTypes = knownTypes

        while not inStream.eof():
            self.stringBlock()
            self.typeBlock()

    @staticmethod
    def newPool(name: str, superPool, types: [], knownTypes):
        raise NotImplementedError()

    def stringBlock(self):
        try:
            count = self.inStream.v64()

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
            n = self.strings.get(self.inStream.v64())
            name: str = n
        except InvalidPoolIndexException as e:
            raise ParseException(self.inStream, self.blockCounter, e, "corrupted type header")

        if name is None:
            raise ParseException(self.inStream, self.blockCounter, None, "corrupted file: nullptr in typename")

        if name in self.seenTypes:
            raise ParseException(self.inStream, self.blockCounter, None, "Duplicate definition of type {}", name)
        self.seenTypes.add(name)

        # try to parse the type definition
        try:
            count = self.inStream.v64()
            # definition: StoragePool = None
            if name in self.poolByName:
                definition: StoragePool = self.poolByName.get(name)
            else:
                restriction = self.inStream.v64()  # typeRestrictions
                superID = self.inStream.v64()
                # superDef: StoragePool = None
                if superID == 0:
                    superDef = None
                elif superID > len(self.types):
                    raise ParseException(self.inStream, self.blockCounter, None,
                                         "Type {} refers to an ill-formed super fType.\n"
                                         + "          found: {}; current number of other types {}",
                                         name, superID, len(self.types))
                else:
                    superDef = self.types[superID - 1]

                try:
                    superType = (SkillObject,) if superDef is None else (superDef._cls,)
                    typ = type(name, superType, dict())
                    subTyp = type("SubType" + name, (typ, NamedType,), dict())
                    definition = self.newPool(name, superDef, self.types, typ, subTyp)
                    if definition.superPool is not superDef:
                        if superDef is None:
                            raise ParseException(self.inStream, self.blockCounter, None,
                                                 "The file contains a super type {}"
                                                 "but {} is specified to be a base type.", "<none>", name)
                        else:
                            raise ParseException(self.inStream, self.blockCounter, None,
                                                 "The file contains a super type {}"
                                                 "but {} is specified to be a base type.", superDef.__name__, name)
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

            bpo = definition.basePool._cachedSize
            if definition.superPool is None:
                bpo += 0
            else:
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
        self.seenTypes.clear()
        self.blockIDBarrier = 0
        self.localFields.clear()
        self.fieldDataQueue.clear()
        self.offset = 0

        # parse type
        count = self.inStream.v64()
        for _ in range(0, count):
            self.typeDefinition()

        # resize pools by updating cachedSize and staticCount
        for e in self.localFields:
            p: StoragePool = e.p
            b: Block = p.lastBlock()
            p._cachedSize += b.count

            if b.count != 0:
                parent: StoragePool = p.superPool
                if parent is not None:
                    sb: Block = parent.lastBlock()
                    delta = sb.staticCount - (b.bpo - sb.bpo)
                    if delta > 0:
                        sb.staticCount -= delta
                        parent.staticDataInstances -= delta

        # parse fields
        for lfe in self.localFields:
            p: StoragePool = lfe.p
            legalFieldIDBarrier = 1 + len(p._dataFields)
            lastBlock: Block = p.blocks[len(p.blocks) - 1]
            for fieldcounter in range(lfe.count, 0, -1):
                ID = self.inStream.v64()
                if ID > legalFieldIDBarrier or ID <= 0:
                    raise ParseException(self.inStream, self.blockCounter, None, "Found an illegal field ID: {}", ID)
                if ID == legalFieldIDBarrier:
                    fieldName = self.strings.get(self.inStream.v64())
                    if fieldName is None:
                        raise ParseException(self.inStream, self.blockCounter, None,
                                             "corrupted file: nullptr in field name")
                    t = self.fieldType()
                    rest = self.inStream.v64()  # fieldRestrictions
                    end = self.inStream.v64()
                    try:
                        f: FieldDeclaration = p.addField(t, fieldName)
                        if len(p.blocks) == 1:
                            f.addChunk(SimpleChunk(self.offset, end, lastBlock.bpo, lastBlock.count))
                        else:
                            f.addChunk(BulkChunk(self.offset, end, p._cachedSize, len(p.blocks)))
                    except SkillException as e:
                        raise ParseException(self.inStream, self.blockCounter, None, e.message)
                    legalFieldIDBarrier += 1
                else:
                    end = self.inStream.v64()
                    p._dataFields[ID - 1].addChunk(SimpleChunk(self.offset, end, lastBlock.bpo, lastBlock.count))

                self.offset = end
                self.fieldDataQueue.append(DataEntry(p, ID))
        self.processFieldData()

    def processFieldData(self):
        fileOffset = self.inStream.position()
        dataEnd = fileOffset
        for e in self.fieldDataQueue:
            f: FieldDeclaration = e.owner._dataFields[e.fieldID - 1]
            end: int = f._addOffsetToLastChunk(fileOffset)
            dataEnd = max(dataEnd, end)
        self.inStream.jump(dataEnd)

    def fieldType(self):
        typeID = self.inStream.v64()
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
            return ConstantLengthArray(self.inStream.v64(), self.fieldType())
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

    def read(self, cls, writeMode, knownTypes):
        try:
            r = cls(self.poolByName, self.strings, self.annotation, self.types, self.inStream, writeMode, knownTypes)
            return r
        except Exception as e:
            raise ParseException(self.inStream, self.blockCounter, e, "State instantiation failed!")
