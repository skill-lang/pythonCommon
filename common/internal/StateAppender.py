from common.internal.WritingFunctions import WritingFunctions
from common.internal.Blocks import SimpleChunk


class StateAppender(WritingFunctions):

    def __init__(self, state, fos):
        super(StateAppender, self).__init__(state)

        i = 0
        for t in state.allTypes():
            if len(t.blocks) == 0:
                break
            i += 1
        newPoolIndex = 0
        self.fixPools(state.allTypes())

        lbpoMap = []
        chunkMap = {}
        bases = 0
        for p in state.allTypes():
            if p.owner is None:
                bases += 1
                p._prepareAppend(lbpoMap, chunkMap)

        # locate relevant pools
        rPools = []
        for p in state.allTypes():
            if (p.typeID() - 32) >= newPoolIndex:
                rPools.append(p)
            elif len(p) > 0:
                exists = False
                for f in p._dataFields:
                    if f in chunkMap:
                        exists = True
                        break
                if exists:
                    rPools.append(p)

        state._strings.prepareAndAppend(fos, self)
        fieldCount = 0
        for f in chunkMap:
            fieldCount += 1
            f._offset = 0
            c = f._lastChunk()
            if isinstance(c, SimpleChunk):
                i = c.bpo
                f._osc(i, i + c.count)
            else:
                f._obc(c)
        fos.v64(fieldCount)

        # write headers
        fieldQueue = []
        stringIDs: [] = state._strings.stringIDs
        for p in rPools:
            newPool = ((p.typeID() - 32) >= newPoolIndex)
            fields = []
            for f in p._dataFields:
                if f in chunkMap:
                    fields.append(f)

            if newPool or (len(fields) != 0 and len(p) > 0):
                self.restrictions(fos)
                fos.v64(stringIDs[p.name()])
                count = p.lastBlock().count
                fos.v64(count)
                if newPool:
                    if p.superName() is None:
                        fos.i8(0)
                    else:
                        fos.v64(p.superPool.typeID() - 31)
                        if count != 0:
                            fos.v64(lbpoMap[p.typeID() - 32] - lbpoMap[p.basePool.typeID() - 32])
                elif p.superName() is not None and count != 0:
                    fos.v64(lbpoMap[p.typeID() - 32] - lbpoMap[p.basePool.typeID() - 32])
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
                fos.v64(f._index)
                if len(f._dataChunks) == 1:
                    fos.v64(stringIDs[f.name()])
                    self.writeType(f.type, fos)
                    self.restrictions(fos)
                end = offset + f._offset
                fos.v64(end)
                data.append(f)
                offset = end
        self.writeFieldData(fos, data)
        # Phase 4
        state._strings.resetIDs()
        self.unfixPools(state.allTypes())
