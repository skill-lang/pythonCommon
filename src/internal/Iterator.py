from src.internal.StoragePool import StoragePool
from src.internal.parts.Blocks import Block


class DynamicDataIterator:

    def __init__(self, storagePool: StoragePool):
        self.p: StoragePool = storagePool
        self.endHeight = storagePool.typeHierarchyHeight
        self.lastBlock = len(storagePool.blocks)
        self.secondIndex = 0
        self.index = 0
        self.last = 0

        while self.index == self.last & self.secondIndex < self.lastBlock:
            b: Block = self.p.get(self.secondIndex)
            self.index = b.bpo
            self.last = self.index + b.count
            self.secondIndex += 1

        if self.index == self.last & self.secondIndex == self.lastBlock:
            self.secondIndex += 1
            while self.p is not None:
                if len(self.p.newObjects) != 0:
                    self.index = 0
                    self.last = len(self.p.newObjects)
                    break
                self.nextP()

    def __iter__(self):
        return self

    def __next__(self):
        if self.secondIndex <= self.lastBlock:
            r = self.p.data[self.index]
            self.index += 1
            if self.index == self.last:
                while self.index == self.last & self.secondIndex < self.lastBlock:
                    b: Block = self.p.blocks.get(self.secondIndex)
                    self.index = b.bpo
                    self.last = self.index + b.count
                    self.secondIndex += 1

                # mode switch, if there is no other block
                if self.index == self.last & self.secondIndex == self.lastBlock:
                    self.secondIndex += 1
                    while self.p is not None:
                        if self.p.newObjects.size() != 0:
                            self.index = 0
                            self.last = self.p.newObjects.size()
                            break
                        self.nextP()
            return r

        r = self.p.newObject(self.index)
        self.index += 1
        if self.index == self.last:
            # do-while: do
            self.nextP()
            if len(self.p.newObjects) != 0:
                self.index = 0
                self.last = len(self.p.newObjects)
            # do-while: while
            while True:
                self.nextP()
                if self.p is None:
                    break
                if len(self.p.newObjects) != 0:
                    self.index = 0
                    self.last = len(self.p.newObjects)
                    break
        return r

    def hasNext(self):
        return self.p is not None

    def nextP(self):
        n: StoragePool = self.p.nextPool()
        if n is not None and self.endHeight < n.typeHierarchyHeight:
            self.p = n
        else:
            self.p = None


class DynamicNewInstancesIterator:

    def __init__(self, storagePool: StoragePool):
        self.ts = TypeHierarchyIterator(storagePool)
        self.last = len(storagePool.newObjects)
        self.index = 0

        while self.last == 0 and self.ts.hasNext():
            self.ts.__next__()
            if self.ts.hasNext():
                self.last = len(self.ts.get().newObjects)
            else:
                return

    def __iter__(self):
        return self

    def __next__(self):
        rval = self.ts.get().newObject(self.index)
        self.index += 1
        if self.index == self.last and self.ts.hasNext():
            self.index = self.last = 0
            # do-while
            self.ts.__next__()
            if self.ts.hasNext():
                self.last = len(self.ts.get().newObjects)
            else:
                return rval

            while self.last == 0 and self.ts.hasNext():
                self.ts.__next__()
                if self.ts.hasNext():
                    self.last = len(self.ts.get().newObjects)
                else:
                    return rval
        return rval

    def hasNext(self):
        return self.index != self.last


class FieldIterator:

    def __init__(self, storagePool: StoragePool):
        self.p = storagePool
        self.i = -len(storagePool.autoFields)
        while self.p is not None and self.i == 0 and len(self.p.dataFields) == 0:
            self.p = self.p.superPool
            if self.p is not None:
                self.i = -len(self.p.autoFields)

    def __iter__(self):
        return self

    def __next__(self):
        if self.i < 0:
            f = self.p.autoFields[-1 - self.i]
        else:
            f = self.p.dataFields[self.i]
        self.i += 1
        if len(self.p.dataFields) == self.i:
            self.p = self.p.superPool
            if self.p is not None:
                self.i = -len(self.p.autoFields)
            while self.p is not None and self.i == 0 and len(self.p.dataFields) == 0:
                self.p = self.p.superPool
                if self.p is not None:
                    self.i = -len(self.p.autoFields)
        return f

    def hasNext(self):
        return self.p is not None


class InterfaceIterator:

    def __init__(self, ps: []):
        self.ps = ps
        self.i = 0
        while self.i < len(self.ps):
            self.xs: DynamicDataIterator = self.ps[self.i].iterator()
            self.i += 1

    def __iter__(self):
        return self

    def __next__(self):
        r = self.xs.__next__()
        if not self.xs.hasNext():
            while self.i < len(self.ps):
                self.xs = self.ps[self.i].iterator()
                self.i += 1
        return r


class StaticDataIterator:

    def __init__(self, storagePool: StoragePool):
        self.p = storagePool
        self.lastBlock = len(storagePool.blocks)
        self.index = self.last = self.secondIndex = 0

        while self.index == self.last and self.secondIndex < self.lastBlock:
            b: Block = self.p.blocks[self.secondIndex]
            self.index = b.bpo
            self.last = self.index + b.staticCount
            self.secondIndex += 1

        if self.index == self.last and self.secondIndex == self.lastBlock:
            self.secondIndex += 1
            self.index = 0
            self.last = len(self.p.newObjects)

    def __iter__(self):
        return self

    def __next__(self):
        if self.secondIndex <= self.lastBlock:
            r = self.p.data[self.index]
            self.index += 1
            if self.index == self.last:
                while self.index == self.last and self.secondIndex < self.lastBlock:
                    b: Block = self.p.blocks[self.secondIndex]
                    self.index = b.bpo
                    self.last = self.index + b.staticCount
                    self.secondIndex += 1

                if self.index == self.last and self.secondIndex == self.lastBlock:
                    self.secondIndex += 1
                    self.index = 0
                    self.last = len(self.p.newObjects)
            return r
        r = self.p.newObject(self.index)
        self.index += 1
        return r

    def hasNext(self):
        return self.index != self.last


class StaticFieldIterator:

    def __init__(self, storagePool: StoragePool):
        if len(storagePool.autoFields) == 0 and len(storagePool.dataFields):
            self.p = None
            self.i = 0
        else:
            self.p = storagePool
            self.i = -len(storagePool.autoFields)

    def __iter__(self):
        return self

    def __next__(self):
        if self.i < 0:
            f = self.p.autoFields[-1 - self.i]
        else:
            f = self.p.dataFields[self.i]
        self.i += 1
        if len(self.p.dataFields) == self.i:
            self.p = None
        return f


class TypeHierarchyIterator:

    def __init__(self, storagePool: StoragePool):
        self.p = storagePool
        self.end = storagePool.typeHierarchyHeight

    def __iter__(self):
        return self

    def __next__(self):
        r = self.p
        n = self.p.nextPool
        if n is None and self.end < n.typeHierarchyHeight:
            self.p = n
        else:
            self.p = None
        return r

    def hasNext(self):
        return self.p is not None

    def get(self):
        return self.p


class TypeOrderIterator:

    def __init__(self, storagePool: StoragePool):
        self.ts = TypeHierarchyIterator(storagePool)
        while self.ts.hasNext():
            t: StoragePool = self.ts.__next__()
            if t.staticSize() != 0:
                self.sdi = StaticDataIterator(t)
                break

    def __iter__(self):
        return self

    def __next__(self):
        result = self.sdi.__next__()
        if not self.sdi.hasNext():
            while self.ts.hasNext():
                t: StoragePool = self.ts.__next__()
                if t.staticSize() != 0:
                    self.sdi = StaticDataIterator(t)
                    break
        return result

    def hasNext(self):
        return
