from src.internal.StateWriter import StateWriter
from src.streams.InStream import InStream
from src.streams.FileInputStream import FileInputStream
from src.streams.FileOutputStream import FileOutputStream
from src.internal.fieldTypes.IntegerTypes import V64
from src.streams.OutStream import OutStream
from src.internal.FieldType import FieldType
import threading
import traceback


class StringPool(FieldType, list):

    typeID = 14
    lock = threading.Lock()

    def __init__(self, inStream: FileInputStream):
        """DO NOT CALL IF YOU ARE NOT GENERATED OR INTERNAL CODE!"""
        super(StringPool, self).__init__(self.typeID)
        self.inStream = inStream
        self.stringPositions = []
        self.stringPositions.append(StringPool.Position(-1, -1))
        self.idMap = [].append(None)
        self.knownStrings = set()
        self.stringIDs = {}

    def readSingleField(self, fis: InStream):
        return self.get(fis.v32())

    def calculateOffset(self, xs):
        if len(self.stringIDs) < 128:
            return len(xs)
        result = 0
        for s in xs:
            if s is None:
                result += 1
            else:
                result += V64().singleOffset(self.stringIDs.get(s))
        return result

    def singleOffset(self, name):
        if name is None:
            return 1
        else:
            return V64().singleOffset(self.stringIDs.get(name))

    def writeSingleField(self, v, out: OutStream):
        if v is None:
            out.i8(0)
        else:
            out.v64(self.stringIDs.get(v))

    def resetIDs(self):
        self.stringIDs.clear()

    def toString(self):
        return "string"

    def size(self):
        return len(self.knownStrings)

    def get(self, index):
        if index is 0:
            return None

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

    def prepareAndWrite(self, out: FileOutputStream, ws: StateWriter):
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
                off += len(self.idMap[i])
                end.append(off)
            for i in range(0, len(end)):
                out.put(end[i])
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
            fos.put(s)

    class Position:

        def __init__(self, l, i):
            self.absoluteOffset = l
            self.length = i
