from src.internal.StoragePool import StoragePool
from src.internal.StringPool import StringPool
import threading
from src.streams.MappedOutputStream import MappedOutputStream
from src.internal.Blocks import *
from src.internal.Exceptions import *
import copy
from src.internal.SkillState import SkillState


class SerializationFunctions:

    def __init__(self, state):
        self.state = state

    @staticmethod
    def collectNestedStrings(strings: StringPool, mapType, xs: {}):
        if xs is not None:
            if mapType.keyType.typeID == 14:
                for s in set(xs.keys):
                    strings.add(s)
            if mapType.valueType.typeID == 14:
                for s in set(xs.values):
                    strings.add(s)
            if mapType.valueType.typeID == 20:
                for s in xs.values:
                    SerializationFunctions.collectNestedStrings(strings, mapType.valueType, s)

    @staticmethod
    def restrictions(pool, outStream):
        outStream.i8(0)

    @staticmethod
    def writeType(t, outStream):
        if t.typeID == 0:
            outStream.i8(0)
            outStream.i8(t.value)
            return
        elif t.typeID == 1:
            outStream.i8(1)
            outStream.i16(t.value)
            return
        elif t.typeID == 2:
            outStream.i8(0)
            outStream.i32(t.value)
            return
        elif t.typeID == 3:
            outStream.i8(0)
            outStream.i64(t.value)
            return
        elif t.typeID == 4:
            outStream.i8(0)
            outStream.v64(t.value)
            return
        elif t.typeID == 15:
            outStream.i8(15)
            outStream.v64(len(t))
            outStream.v64(t.groundType.typeID)
            return
        elif t.typeID == 19:
            outStream.i8(t.typeID)
            outStream.v64(t.groundType.typeID)
            return
        elif t.typeID == 20:
            outStream.i8(20)
            SerializationFunctions.writeType(t.keyType, outStream)
            SerializationFunctions.writeType(t.valueType, outStream)
            return
        else:
            outStream.v64(t.typeID)
            return

    @staticmethod
    def writeFieldData(state, fos, data: [], offset, barrier: threading.Semaphore):
        writeErrors = []
        writeMap: MappedOutputStream = fos.mapBlock(offset)

        for t in data:
            t.outMap = copy.deepcopy(writeMap)
            t.writeErrors = writeErrors
            t.barrier = barrier
            SkillState.threadPool.execute(t)
        for _ in range(len(data)):
            barrier.acquire()
        writeMap.close()
        fos.close()

        for e in writeErrors:
            raise e
        if len(writeErrors) != 0:
            raise writeErrors.pop(0)

        # Phase 4
        state.strings.resetIDs()
        StoragePool.unfixPools(state.types)


class Task(threading.Thread):

    outMap: MappedOutputStream
    writeErrors = []
    barrier = threading.Semaphore(0)

    def __init__(self, f, begin, end):
        super(Task, self).__init__()
        self.f = f
        self.begin = begin
        self.end = end

    def run(self):
        try:
            c = self.f.lastChunk()
            if isinstance(c, SimpleChunk):
                i = c.bpo
                self.f.wsc(i, i + c.count, self.outMap)
            else:
                self.f.wbc(c, self.outMap)
        except SkillException as s:
            self.writeErrors.append(s)
        except IOError as i:
            self.writeErrors.append(SkillException("failed to write field " + self.f.toString(), i))
        except Exception as e:
            self.writeErrors.append(SkillException("unexpected failure while writing field []".format(
                self.f.toString()), e))
        finally:
            self.barrier.release()
