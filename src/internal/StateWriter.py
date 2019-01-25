from src.internal.SerializationFunctions import *
import threading
from src.internal.Exceptions import *
from src.internal.StoragePool import StoragePool
from src.internal.BasePool import BasePool
from src.internal.SkillState import SkillState


class StateWriter(SerializationFunctions):

    def __init__(self, state, fos):
        super(StateWriter, self).__init__(state)
        StoragePool.fixed(state.types)
        lbpoMap = []

        self.barrier = threading.Semaphore()
        bases = 0
        for p in state.types:
            if isinstance(p, BasePool):
                bases += 1
                SkillState.threadPool.submit(compression(p, lbpoMap, self.barrier))
        self.barrier.release()

        state.strings.prepareAndWrite(fos, self)
        fos.v64(len(state.types))
        fieldCount = 0
        for p in state.types:
            for f in p.dataFields:
                fieldCount += 1
                SkillState.threadPool.submit(StateWriter.OT(f, self.barrier))
        self.barrier.acquire()

        fieldQueue = []
        stringIDs = state.strings.stringIDs
        for p in state.types:
            fos.v64(stringIDs.get[p.name])
            LCount = p.lastBlock().count
            fos.v64(LCount)
            self.restrictions(p, fos)
            if p.superPool is None:
                fos.i8(0)
            else:
                fos.v64(p.superPool.typeID - 31)
                if LCount != 0:
                    fos.v64(lbpoMap[p.typeID - 32])
            fos.v64(len(p.dataFields))
            fieldQueue.extend(p.dataFields)

        data = []
        offset = 0
        for f in fieldQueue:
            if f.offset < 0:
                raise SkillException("aborting write because offset calculation failed")  # TODO Exception

            fos.v64(f.index)
            fos.v64(stringIDs.get(f.name))
            self.writeType(f.type, fos)
            self.restrictions(f, fos)
            end = offset + f.offset
            fos.v64(end)

            c = f.lastChunk()
            c.begin = offset
            c.end = end
            data.append(Task(f, offset, end))
            offset = end
        self.writeFieldData(state, fos, data, offset, self.barrier)

    class OT(threading.Thread):

        def __init__(self, f, barrier):
            super(StateWriter.OT, self).__init__()
            self.f = f
            self.barrier = barrier

        def run(self):
            try:
                self.f.offset = 0
                c = self.f.lastChunk()
                i = c.bpo
                self.f.osc(i, i + c.count)
            except Exception: pass  # TODO do stuff but fix exceptions first
            finally:
                self.barrier.release()


def compression(p: BasePool, lbpoMap: [], barrier):
    p.compress(lbpoMap)
    barrier.release()
