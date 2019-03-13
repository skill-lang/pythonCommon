import sys
import traceback

from common.internal.SerializationFunctions import SerializationFunctions, Task
import threading
from common.internal.Exceptions import SkillException
from common.internal.threadpool import threadPool
from common.internal.BasePool import BasePool


class StateWriter(SerializationFunctions):

    def __init__(self, state, fos):
        super(StateWriter, self).__init__(state)
        self.fixPools(state.types)
        lbpoMap = [0 in range(0, len(state.types))]

        self.barrier = threading.Semaphore(0)
        bases = 0
        for p in state.types:
            if isinstance(p, BasePool):
                bases += 1
                threadPool.submit(compression(p, lbpoMap, self.barrier))
        for _ in range(bases):
            self.barrier.acquire()

        state.strings.prepareAndWrite(fos, self)
        fos.v64(len(state.types))
        fieldCount = 0
        for p in state.types:
            for f in p.dataFields:
                fieldCount += 1
                threadPool.submit(StateWriter.OT(f, self.barrier).run())
        for _ in range(fieldCount):
            self.barrier.acquire()

        fieldQueue = []
        stringIDs = state.strings.stringIDs
        for p in state.types:
            fos.v64(stringIDs[p.name])
            LCount = p.lastBlock().count
            fos.v64(LCount)
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
                raise SkillException("aborting write because offset calculation failed")

            fos.v64(f.index)
            fos.v64(stringIDs.get(f.name))
            self.writeType(f.fType, fos)
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
            except:
                traceback.print_exc()
                print("Offset calculation failed, resulting file will be corrupted.")
                self.f.offset = -sys.maxsize - 1
            finally:
                self.barrier.release()


def compression(p, lbpoMap: [], barrier):
    p.compress(lbpoMap)
    barrier.release()
