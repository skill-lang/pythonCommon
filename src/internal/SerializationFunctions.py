import threading
from src.internal.Blocks import SimpleChunk
from src.internal.Exceptions import SkillException
import copy
from src.streams.MappedOutputStream import MappedOutputStream
from src.internal.threadpool import threadPool


class SerializationFunctions:

    def __init__(self, state):
        self.state = state

        strings = state.strings
        for p in state.types:
            strings.add(p.name)
            for f in p.dataFields:
                strings.add(f.name)

                if f.fType.typeID == 14:
                    for i in p:
                        if not i.isDeleted():
                            strings.add(i.get(f))

                if f.fType.typeID in [15, 17, 18, 19]:
                    if f.fType.groundType.typeID == 14:
                        for i in p:
                            if not i.isDeleted():
                                xs = i.get(f)
                                for s in xs:
                                    strings.add(s)

                if f.fType.typeID == 20:
                    typ = f.fType
                    k = typ.keyType.typeID == 14
                    v = typ.valueType.typeID == 14
                    if k or v:
                        for i in p:
                            if not i.isDeleted():
                                xs = i.get(f)
                                if xs is not None:
                                    if k:
                                        for s in xs:
                                            strings.add(s)
                                    if v:
                                        for s in xs.values():
                                            strings.add(s)
                    if typ.valueType.typeID == 20:
                        nested = typ.valueType
                        if nested.keyType == 14 or nested.valueType.typeID == 14 or nested.valueType.typeID == 20:
                            for i in p:
                                if not i.isDeleted():
                                    self.collectNestedStrings(strings, typ, i.get(f))

                if f.isLazy:
                    f.ensureLoaded()
                if f.isDistributed:
                    f.compress()
        state.strings.resetIDs()

    @staticmethod
    def collectNestedStrings(strings, mapType, xs: {}):
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
        elif t.typeID in [17, 18, 19]:
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

    def writeFieldData(self, state, fos, data: [], offset, barrier: threading.Semaphore):
        writeErrors = []
        writeMap = fos.mapBlock(offset)

        for t in data:
            t.outMap = copy.deepcopy(writeMap)
            t.writeErrors = writeErrors
            t.barrier = barrier
            threadPool.execute(t)
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
        self.unfixPools(state.types)

    @staticmethod
    def fixPools(pools: []):
        for p in pools:
            p.cachedSize = p.staticSize() - p.deletedCount
            p.fixed = True

        for i in range(len(pools), -1, -1):
            p = pools[i]
            if p.superPool is not None:
                p.superPool.cachedSize += p.cachedSize

    @staticmethod
    def unfixPools(pools: []):
        for p in pools:
            p.fixed = False


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
