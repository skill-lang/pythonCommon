from common.internal.StateWriter import StateWriter
from common.streams.InStream import InStream
from common.streams.FileInputStream import FileInputStream
from common.internal.fieldTypes.IntegerTypes import V64
from common.streams.OutStream import OutStream
from common.internal.FieldType import FieldType
import threading
from typing import TypeVar

S = TypeVar('S', FileInputStream, type(None))


class StringPool(FieldType):

    _typeID = 14
    lock = threading.Lock()

    def __init__(self, inStream: S):
        """DO NOT CALL IF YOU ARE NOT GENERATED OR INTERNAL CODE!"""
        super(StringPool, self).__init__(self._typeID)
        self.inStream = inStream
        self.stringPositions = []
        self.stringPositions.append(StringPool.Position(-1, -1))
        self.idMap = []
        self.idMap.append(None)
        self.knownStrings = set()
        self.stringIDs = {}

    def readSingleField(self, fis: InStream): return self.get(fis.v64())

    def calculateOffset(self, xs):
        if len(self.stringIDs) < 128:
            return len(xs)
        result = 0
        for s in xs:
            if s is None:
                result += 1
            else:
                result += V64().singleV64Offset(self.stringIDs.get(s))
        return result

    def singleOffset(self, name):
        if name is None:
            return 1
        else:
            return V64().singleV64Offset(self.stringIDs.get(name))

    def writeSingleField(self, v, out: OutStream):
        if v is None:
            out.i8(0)
        else:
            out.v64(self.stringIDs.get(v))

    def resetIDs(self): self.stringIDs.clear()

    def __str__(self): return "string"

    def size(self): return len(self.knownStrings)

    def __len__(self): return len(self.knownStrings)

    def get(self, index):
        if index is 0:
            return None
        result = None
        try:
            result = self.idMap[index]
        except IndexError:
            raise Exception
        if result is not None:
            return result

        with self.lock:
            off: StringPool.Position = self.stringPositions[index]
            self.inStream.push(off.absoluteOffset)
            chars = self.inStream.bytes(off.length)
            self.inStream.pop()
            result = chars.decode('utf-8')

            self.idMap[index] = result
            self.knownStrings.add(result)
        return result

    def prepareAndWrite(self, out, ws: StateWriter):
        self.idMap.clear()
        self.idMap.append(None)

        for s in self.knownStrings:
            if not(s in list(self.stringIDs)):
                self.stringIDs[s] = len(self.idMap)
                self.idMap.append(s)

        count = len(self.idMap) - 1
        out.v64(count)
        if count != 0:
            off = 0
            end = []
            for i in range(1, count + 1):
                off += len(self.idMap[i].encode())  # the warning is wrong because idMap is filled with strings
                end.append(off)
            for i in range(0, len(end)):
                out.i32(end[i])
            for i in range(1, count + 1):
                out.put(self.idMap[i].encode())

    def prepareAndAppend(self, fos, sa):
        for i in range(1, len(self.idMap)):
            self.stringIDs[self.idMap[i]] = i
        todo = []

        for s in self.knownStrings:
            if s not in self.stringIDs:
                self.stringIDs[s] = len(self.idMap)
                self.idMap.append(s)
                todo.append(bytearray(s.encode('utf-8')))

        count = len(todo)
        fos.v64(count)

        off = 0
        end = []
        for s in todo:
            off += len(s)
            end.append(off)
        fos.put(end)
        for s in todo:
            fos.putString(s)

    def contains(self, obj): return obj in self.knownStrings

    def __iter__(self): return self.knownStrings.__iter__()

    def toArray(self): return list(self.knownStrings)

    def add(self, e):
        self.knownStrings.add(e)

    def remove(self, obj): self.knownStrings.remove(obj)

    def containsAll(self, c):
        for x in c:
            if x not in self.knownStrings:
                return False
        return True

    def addAll(self, c): self.knownStrings.update(c)

    def removeAll(self, c):
        for x in c:
            if x in self.knownStrings:
                self.knownStrings.remove(x)

    def retainAll(self, c):
        for x in self.knownStrings:
            if x not in c:
                self.knownStrings.remove(x)

    def clear(self): self.knownStrings.clear()

    def hasInStream(self): return self.inStream is not None

    class Position:

        def __init__(self, l, i):
            self.absoluteOffset = l
            self.length = i