import threading
from common.internal.Blocks import SimpleChunk
from common.internal.Exceptions import SkillException


class SerializationFunctions:

    def __init__(self, state):
        self.state = state

        strings = self.state.Strings()
        for p in self.state.allTypes():
            strings.add(p.name())
            for f in p._dataFields:
                strings.add(f.name())

                if f.fieldType().typeID() == 14:
                    for i in p:
                        if not i.isDeleted():
                            strings.add(i.get(f))

                if f.fieldType().typeID() in [15, 17, 18, 19]:
                    if f.fieldType().groundType.typeID() == 14:
                        for i in p:
                            if not i.isDeleted():
                                xs = i.get(f)
                                for s in xs:
                                    strings.add(s)

                if f.fieldType().typeID() == 20:
                    typ = f.fieldType()
                    k = typ.keyType.typeID() == 14
                    v = typ.valueType.typeID() == 14
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
                    if typ.valueType.typeID() == 20:
                        nested = typ.valueType
                        if nested.keyType == 14 or nested.valueType.typeID() == 14 or nested.valueType.typeID() == 20:
                            for i in p:
                                if not i.isDeleted():
                                    self.collectNestedStrings(strings, typ, i.get(f))

                if f.isLazy:
                    f._ensureLoaded()
                if f.isDistributed:
                    f._compress()
        self.state._strings.resetIDs()

    @staticmethod
    def collectNestedStrings(strings, mapType, xs: {}):
        if xs is not None:
            if mapType.keyType.typeID() == 14:
                for s in set(xs.keys):
                    strings.add(s)
            if mapType.valueType.typeID() == 14:
                for s in set(xs.values):
                    strings.add(s)
            if mapType.valueType.typeID() == 20:
                for s in xs.values:
                    SerializationFunctions.collectNestedStrings(strings, mapType.valueType, s)

    @staticmethod
    def writeType(t, outStream):
        if t.typeID() == 0:
            outStream.i8(0)
            outStream.i8(t.value())
            return
        elif t.typeID() == 1:
            outStream.i8(1)
            outStream.i16(t.value())
            return
        elif t.typeID() == 2:
            outStream.i8(0)
            outStream.i32(t.value())
            return
        elif t.typeID() == 3:
            outStream.i8(0)
            outStream.i64(t.value())
            return
        elif t.typeID() == 4:
            outStream.i8(0)
            outStream.v64(t.value())
            return
        elif t.typeID() == 15:
            outStream.i8(15)
            outStream.v64(len(t))
            outStream.v64(t.groundType.typeID())
            return
        elif t.typeID() in [17, 18, 19]:
            outStream.i8(t.typeID())
            outStream.v64(t.groundType.typeID())
            return
        elif t.typeID() == 20:
            outStream.i8(20)
            SerializationFunctions.writeType(t.keyType, outStream)
            SerializationFunctions.writeType(t.valueType, outStream)
            return
        else:
            outStream.v64(t.typeID())
            return

    def writeFieldData(self, state, fos, data: [], offset, barrier: threading.Semaphore):
        writeErrors = []

        for t in data:
            t.outMap = fos
            t.writeErrors = writeErrors
            t.barrier = barrier
            t.run()
        for _ in range(len(data)):
            barrier.acquire()
        fos.close()

        for e in writeErrors:
            raise e
        if len(writeErrors) != 0:
            raise writeErrors.pop(0)

        # Phase 4
        state._strings.resetIDs()
        self.unfixPools(state.allTypes())

    @staticmethod
    def fixPools(pools: []):
        for p in pools:
            p._cachedSize = p.staticSize() - p._deletedCount
            p.fixed = True

        for i in range(len(pools) - 1, -1, -1):
            p = pools[i]
            if p.superPool is not None:
                p.superPool._cachedSize += p._cachedSize

    @staticmethod
    def unfixPools(pools: []):
        for p in pools:
            p.fixed = False

    @staticmethod
    def restrictions(outStream):
        outStream.i8(0)


class Task(threading.Thread):

    writeErrors = []
    barrier: threading.Semaphore

    def __init__(self, f, begin, end):
        super(Task, self).__init__()
        self.f = f
        self.begin = begin
        self.end = end
        self.outMap = None

    def run(self):
        try:
            c = self.f._lastChunk()
            if isinstance(c, SimpleChunk):
                i = c.bpo
                self.f._wsc(i, i + c.count, self.outMap)
            else:
                self.f._wbc(c, self.outMap)
        except SkillException as s:
            self.writeErrors.append(s)
        except IOError as i:
            self.writeErrors.append(SkillException("failed to write field " + self.f.__str__(), i))
        except Exception as e:
            self.writeErrors.append(SkillException("unexpected failure while writing field {}".format(
                self.f.__str__()), e))
        finally:
            self.barrier.release()
