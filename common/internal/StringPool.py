from common.internal.StateWriter import StateWriter
from common.streams.InStream import InStream
from common.streams.FileInputStream import FileInputStream
from common.internal.fieldTypes.IntegerTypes import V64
from common.streams.OutStream import OutStream
from common.internal.FieldType import FieldType
from typing import TypeVar

S = TypeVar('S', FileInputStream, type(None))


class StringPool(FieldType):
    """
    Container for all Strings.
    """

    _typeID = 14

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

    def readSingleField(self, fis: InStream):
        """
        Return a string hold by this StringPool by reading the index from the file.
        :param fis: FileInputStream
        :return: String hold by this StringPool
        """
        return self.get(fis.v64())

    def calculateOffset(self, xs):
        """
        Calculates offset of all strings in collection xs.
        :param xs: Collection of strings
        :return: offset
        """
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
        """
        Calculates offset of the id of the string with the specified name
        :param name: name of the string
        :return: offset of the id
        """
        if name is None:
            return 1
        else:
            return V64().singleV64Offset(self.stringIDs.get(name))

    def writeSingleField(self, v, out: OutStream):
        """
        Writes the id of the string to the file.
        :param v: string
        :param out: FileOutputStream
        :return:
        """
        if v is None:
            out.i8(0)
        else:
            out.v64(self.stringIDs.get(v))

    def resetIDs(self): self.stringIDs.clear()

    def __str__(self): return "string"

    def size(self): return len(self.knownStrings)

    def __len__(self): return len(self.knownStrings)

    def get(self, index):
        """
        Get a string by its id.
        :param index: id of the string
        :return: string
        """
        if index is 0:
            return None
        result = None
        try:
            result = self.idMap[index]
        except IndexError:
            raise Exception
        if result is not None:
            return result

        off: StringPool.Position = self.stringPositions[index]
        self.inStream.push(off.absoluteOffset)
        chars = self.inStream.bytes(off.length)
        self.inStream.pop()
        result = chars.decode('utf-8')

        self.idMap[index] = result
        self.knownStrings.add(result)
        return result

    def prepareAndWrite(self, outStream, ws: StateWriter):
        """
        Update dict and list of strings and writes offsets and string to the file.
        :param outStream: FileOutputStream
        :param ws: StateWriter
        :return:
        """
        self.idMap.clear()
        self.idMap.append(None)

        for s in self.knownStrings:
            try:
                a = self.stringIDs[s]
            except:
                a = None
            if a is None:
                self.stringIDs[s] = len(self.idMap)
                self.idMap.append(s)

        count = len(self.idMap) - 1
        outStream.v64(count)
        if count != 0:
            off = 0
            end = []
            for i in range(1, count + 1):
                off += len(self.idMap[i].encode())
                end.append(off)
            for i in range(0, len(end)):
                outStream.i32(end[i])
            for i in range(1, count + 1):
                outStream.put(self.idMap[i].encode())

    def prepareAndAppend(self, fos, sa):
        """
        Update dict and list of strings and appends offsets and string in a new string block to the file.
        :param fos: FileOutputStream
        :param sa: StateAppender
        :return:
        """
        for i in range(1, len(self.idMap)):
            self.stringIDs[self.idMap[i]] = i
        todo = []

        for s in self.knownStrings:
            try:
                a = self.stringIDs[s]
            except:
                a = None
            if a is None:
                self.stringIDs[s] = len(self.idMap)
                self.idMap.append(s)
                todo.append(bytes(s.encode('utf-8')))

        count = len(todo)
        fos.v64(count)

        off = 0
        end = bytearray()
        for s in todo:
            off += len(s)
            end.append(off)
        fos.put(end)
        for s in todo:
            fos.putString(s)

    def contains(self, obj):
        """
        :param obj: string
        :return: True iff string in this StringPool, else False
        """
        return obj in self.knownStrings

    def __iter__(self):
        """
        Iterator over all known strings
        :return:
        """
        return self.knownStrings.__iter__()

    def toList(self):
        """
        :return: list of all known strings without duplicates.
        """
        return list(self.knownStrings)

    def add(self, e):
        """
        Adds string to StringPool
        :param e: string to add
        :return:
        """
        self.knownStrings.add(e)

    def remove(self, obj):
        """
        Removes string from StringPool
        :param obj: string to remove
        :return:
        """
        self.knownStrings.remove(obj)

    def containsAll(self, c):
        """
        :param c: collection
        :return: True iff all strings in c are in this StringPool, else False
        """
        for x in c:
            if x not in self.knownStrings:
                return False
        return True

    def addAll(self, c):
        """
        Adds all strings in c to the StringPool
        :param c: collection
        :return:
        """
        self.knownStrings.update(c)

    def removeAll(self, c):
        """
        Removes all strings stored in c from this StringPool.
        :param c: collection of strings
        :return:
        """
        for x in c:
            if x in self.knownStrings:
                self.knownStrings.remove(x)

    def retainAll(self, c):
        """
        Removes all strings from this StringPool except the ones in c.
        :param c: collection of strings
        :return:
        """
        for x in self.knownStrings:
            if x not in c:
                self.knownStrings.remove(x)

    def clear(self):
        """
        Clears knownStrings of this StringPool
        :return:
        """
        self.knownStrings.clear()

    def hasInStream(self):
        """
        :return: True if StringPool has a FileInputStream
        """
        return self.inStream is not None

    class Position:
        """
        Position of a string in the file. This stores the offset and the length of a string.
        """
        def __init__(self, l, i):
            self.absoluteOffset = l
            self.length = i
