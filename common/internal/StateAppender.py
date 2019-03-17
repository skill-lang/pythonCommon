from common.internal.SerializationFunctions import SerializationFunctions, Task
from common.internal.Blocks import SimpleChunk
from threading import Semaphore
from common.internal.threadpool import threadPool


class StateAppender(SerializationFunctions):

    def __init__(self, state, fos):
        super(StateAppender, self).__init__(state)

        i = 0
        for t in state.types:
            if len(t.blocks) == 0:
                break
            i += 1
        newPoolIndex = 0
        self.fixPools(state.types)

        lbpoMap = []
        chunkMap = {}
        barrier = Semaphore(0)
        bases = 0
        for p in state.types:
            if p.owner is None:
                bases += 1
                threadPool.submit(parallelRun1, p, lbpoMap, chunkMap, barrier)
        for _ in range(bases):
            barrier.acquire()

        # locate relevant pools
        rPools = []
        for p in state.types:
            if (p.typeID - 32) >= newPoolIndex:
                rPools.append(p)
            elif len(p) > 0:
                exists = False
                for f in p.dataFields:
                    if f in chunkMap:
                        exists = True
                        break
                if exists:
                    rPools.append(p)

        state.strings.prepareAndAppend(fos, self)
        fieldCount = 0
        for f in chunkMap:
            fieldCount += 1
            threadPool.submit(parallelRun2, f, barrier)
        for _ in range(fieldCount):
            barrier.acquire()
        fos.v64(fieldCount)

        # write headers
        fieldQueue = []
        stringIDs: [] = state.strings.stringIDs
        for p in rPools:
            newPool = ((p.typeID - 32) >= newPoolIndex)
            fields = []
            for f in p.dataFields:
                if f in chunkMap:
                    fields.append(f)

            if newPool or (len(fields) != 0 and len(p) > 0):
                self.restrictions(fos)
                fos.v64(stringIDs[p.name])
                count = p.lastBlock().count
                fos.v64(count)
                if newPool:
                    if p.superName() is None:
                        fos.i8(0)
                    else:
                        fos.v64(p.superPool.typeID - 31)
                        if count != 0:
                            fos.v64(lbpoMap[p.typeID - 32] - lbpoMap[p.basePool.typeID - 32])
                elif p.superName() is not None and count != 0:
                    fos.v64(lbpoMap[p.typeID - 32] - lbpoMap[p.basePool.typeID - 32])
                if newPool and count == 0:
                    fos.i8(0)
                else:
                    fos.v64(len(fields))
                    fieldQueue.append(fields)

        # write fields
        data = []
        offset = 0
        for fie in fieldQueue:
            for f in fie:
                fos.v64(f.index)
                if len(f.dataChunks) == 1:
                    fos.v64(stringIDs[f.name])
                    self.writeType(f.type, fos)
                    self.restrictions(fos)
                end = offset + f.offset
                fos.v64(end)
                data.append(Task(f, offset, end))
                offset = end
        self.writeFieldData(state, fos, data, offset, barrier)


def parallelRun1(p, lbpoMap, chunkMap, barrier):
    p.prepareAppend(lbpoMap, chunkMap)
    barrier.release()


def parallelRun2(f, barrier):
    f.offset = 0
    c = f.lastChunk()
    if isinstance(c, SimpleChunk):
        i = c.bpo
        f.osc(i, i + c.count)
    else:
        f.obc(c)
    barrier.release()
