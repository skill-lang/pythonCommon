from src.internal.SerializationFunctions import *
from src.internal.SkillState import SkillState
from src.internal.StoragePool import StoragePool
from src.internal.BasePool import BasePool
from src.internal.Blocks import *
from src.streams.FileOutputStream import FileOutputStream
import threading


class StateAppender(SerializationFunctions):

    def __init__(self, state: SkillState, fos: FileOutputStream):
        super(StateAppender, self).__init__(state)

        i = 0
        for t in  state.types:
            if len(t.blocks) == 0:
                break
            i += 1
        newPoolIndex = 0
        StoragePool.fixed(state.types)

        lbpoMap = []
        chunkMap = {}
        barrier = threading.Semaphore()
        bases = 0
        for p in state.types:
            if isinstance(p, BasePool):
                bases += 1
                SkillState.threadPool.submit(parallelRun1, p, lbpoMap, chunkMap, barrier)
        barrier.release()

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
            SkillState.threadPool.submit(parallelRun2, f, barrier)
        barrier.acquire()
        fos.v64(fieldCount)
        fieldQueue = []
        stringIDs: [] = state.strings.stringIDs
        for p in rPools:
            newPool = ((p.typeID - 32) >= newPoolIndex)
            fields = []
            for f in p.dataFields:
                if f in chunkMap:
                    fields.append(f)

            if newPool or (len(fields) != 0 and len(p) > 0):
                fos.v64(stringIDs[p.name])
                count = p.lastBlock().count
                fos.v64(count)
                if newPool:
                    self.restrictions(p, fos)
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

        data = []
        offset = 0
        for fie in fieldQueue:
            for f in fie:
                fos.v64(f.index)
                if len(f.dataChunks) == 1:
                    fos.v64(stringIDs[f.name])
                    self.writeType(f.type, fos)
                    self.restrictions(f, fos)
                end = offset + f.offset
                fos.v64(end)
                data.append(Task(f, offset, end))
                offset = end
        self.writeFieldData(state, fos, data, offset, barrier)


def parallelRun1(p: BasePool, lbpoMap, chunkMap, barrier):
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
