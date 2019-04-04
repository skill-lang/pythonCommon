import sys
import traceback

from common.internal.SerializationFunctions import SerializationFunctions, Task
import threading
from common.internal.Exceptions import SkillException
from common.internal.BasePool import BasePool


class StateWriter(SerializationFunctions):

    def __init__(self, state, fos):
        super(StateWriter, self).__init__(state)
        self.fixPools(state.allTypes())
        lbpoMap = [0 for i in range(0, len(state.allTypes()))]

        self.barrier = threading.Semaphore(0)
        bases = 0
        for p in state.allTypes():
            if isinstance(p, BasePool):
                bases += 1
                p._compress(lbpoMap)
                self.barrier.release()
        for _ in range(bases):
            self.barrier.acquire()

        # **************** Phase 3: Write ******************
        # write string block
        state._strings.prepareAndWrite(fos, self)
        fos.v64(len(state.allTypes()))
        fieldCount = 0
        for p in state.allTypes():
            for f in p._dataFields:
                fieldCount += 1
                StateWriter.OT(f, self.barrier).run()
        for _ in range(fieldCount):
            self.barrier.acquire()

        # write types
        fieldQueue = []
        stringIDs = state._strings.stringIDs
        for p in state.allTypes():
            fos.v64(stringIDs[p.name()])
            LCount = p.lastBlock().count
            fos.v64(LCount)
            self.restrictions(fos)
            if p.superPool is None:
                fos.i8(0)
            else:
                fos.v64(p.superPool.typeID() - 31)
                if LCount != 0:
                    fos.v64(lbpoMap[p.typeID() - 32])
            fos.v64(len(p._dataFields))
            fieldQueue.extend(p._dataFields)

        # write fields
        data = []
        offset = 0
        for f in fieldQueue:
            if f._offset < 0:
                raise SkillException("aborting write because offset calculation failed")

            fos.v64(f.index)
            fos.v64(stringIDs.get(f.name()))
            self.writeType(f.fieldType(), fos)
            self.restrictions(fos)
            end = offset + f._offset
            fos.v64(end)

            # write instances
            c = f._lastChunk()
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
                self.f._offset = 0
                c = self.f._lastChunk()
                i = c.bpo
                self.f._osc(i, i + c.count)
            except:
                traceback.print_exc()
                print("Offset calculation failed, resulting file will be corrupted.")
                self.f._offset = -sys.maxsize - 1
            finally:
                self.barrier.release()
