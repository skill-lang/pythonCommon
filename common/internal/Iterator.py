
class DynamicDataIterator:
    """
    Iterates over all instances of the StoragePools which are iterated in Pre-order.
    """

    def __init__(self, storagePool):
        """
        :param storagePool: first StoragePools
        """
        self.p = storagePool
        self.endHeight = storagePool.typeHierarchyHeight
        self.lastBlock = len(storagePool.blocks)
        self.secondIndex = 0
        self.index = 0
        self.last = 0

        while self.index == self.last and self.secondIndex < self.lastBlock:
            b = self.p.blocks[self.secondIndex]
            self.index = b.bpo
            self.last = self.index + b.count
            self.secondIndex += 1

        if self.index == self.last and self.secondIndex == self.lastBlock:
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
        if self.p is None:
            raise StopIteration()
        if self.secondIndex <= self.lastBlock:
            r = self.p.data()[self.index]
            self.index += 1
            if self.index == self.last:
                while self.index == self.last and self.secondIndex < self.lastBlock:
                    b = self.p.blocks[self.secondIndex]
                    self.index = b.bpo
                    self.last = self.index + b.count
                    self.secondIndex += 1

                # mode switch, if there is no other block
                if self.index == self.last and self.secondIndex == self.lastBlock:
                    self.secondIndex += 1
                    while self.p is not None:
                        if len(self.p.newObjects) != 0:
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
            if self.p is None:
                return r
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

    def nextP(self):
        n = self.p.nextPool()
        if n is not None and self.endHeight < n.typeHierarchyHeight:
            self.p = n
        else:
            self.p = None


class DynamicNewInstancesIterator:
    """
    Iterates over all new instances in a StoragePool.
    """

    def __init__(self, storagePool):
        """
        :param storagePool: StoragePool which holds the instances.
        """
        self.ts = TypeHierarchyIterator(storagePool)
        self.last = len(storagePool.newObjects)
        self.index = 0

        while self.last == 0 and self.ts.hasNext():
            self.ts.__next__()
            if self.ts.hasNext():
                self.last = len(self.ts.p.newObjects)
            else:
                return

    def __iter__(self):
        return self

    def __next__(self):
        if self.index == self.last:
            raise StopIteration()
        rval = self.ts.p.newObject(self.index)
        self.index += 1
        if self.index == self.last:
            try:
                self.ts.__next__()
            except StopIteration:
                raise StopIteration
            self.index = self.last = 0
            for t in self.ts:
                self.rval = t
        return rval

    def hasNext(self):
        return self.index != self.last


class FieldIterator:
    """
    Iterates over all FieldDeclaration of a StoragePool and its superpools.
    """

    def __init__(self, storagePool):
        self.p = storagePool
        self.i = -len(storagePool._autoFields)
        while self.p is not None and self.i == 0 and len(self.p._dataFields) == 0:
            self.p = self.p.superPool
            if self.p is not None:
                self.i = -len(self.p._autoFields)

    def __iter__(self):
        return self

    def __next__(self):
        if self.p is None:
            raise StopIteration()
        if self.i < 0:
            f = self.p._autoFields[-1 - self.i]
        else:
            f = self.p._dataFields[self.i]
        self.i += 1
        if len(self.p._dataFields) == self.i:
            self.p = self.p.superPool
            if self.p is not None:
                self.i = -len(self.p._autoFields)
            while self.p is not None and self.i == 0 and len(self.p._dataFields) == 0:
                self.p = self.p.superPool
                if self.p is not None:
                    self.i = -len(self.p._autoFields)
        return f


class StaticDataIterator:
    """
    Iterates over all instances in a StoragePool.
    """

    def __init__(self, storagePool):
        """
        :param storagePool: StoragePool which holds the FieldDeclarations
        """
        self.p = storagePool
        self.lastBlock = len(storagePool.blocks)
        self.index = 0
        self.last = 0
        self.secondIndex = 0

        while self.index == self.last and self.secondIndex < self.lastBlock:
            b = self.p.blocks[self.secondIndex]
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
        if self.index == self.last:
            raise StopIteration()
        if self.secondIndex <= self.lastBlock:
            r = self.p.data()[self.index]
            self.index += 1
            if self.index == self.last:
                while self.index == self.last and self.secondIndex < self.lastBlock:
                    b = self.p.blocks[self.secondIndex]
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


class StaticFieldIterator:
    """
    Iterates over FieldDeclarations of a StoragePool without its superpools.
    """

    def __init__(self, storagePool):
        """
        :param storagePool: StoragePool which holds the FieldDeclarations
        """
        if len(storagePool._autoFields) == 0 and len(storagePool._dataFields) == 0:
            self.p = None
            self.i = 0
        else:
            self.p = storagePool
            self.i = -len(storagePool._autoFields)

    def __iter__(self):
        return self

    def __next__(self):
        if self.p is None:
            raise StopIteration()
        if self.i < 0:
            f = self.p._autoFields[-1 - self.i]
        else:
            f = self.p._dataFields[self.i]
        self.i += 1
        if len(self.p._dataFields) == self.i:
            self.p = None
        return f


class TypeHierarchyIterator:
    """
    Iterates over all StoragePools in Pre-order.
    """

    def __init__(self, storagePool):
        """
        :param storagePool: first StoragePool
        """
        self.p = storagePool
        self.end = storagePool.typeHierarchyHeight

    def __iter__(self):
        return self

    def __next__(self):
        if self.p is None:
            raise StopIteration()
        r = self.p
        n = self.p._nextPool
        if n is not None and self.end < n.typeHierarchyHeight:
            self.p = n
        else:
            self.p = None
        return r

    def hasNext(self):
        return self.p is not None


class TypeOrderIterator:
    """
    Iterates over instances in StoragePools which are iterated in type order.
    """

    def __init__(self, storagePool):
        """
        :param storagePool: first StoragePool
        """
        self.sdi = None
        self.ts = TypeHierarchyIterator(storagePool)
        self.lastTS = None
        for t in self.ts:
            if t.staticSize() != 0:
                self.sdi = StaticDataIterator(t)
                self.lastTS = t
                break

    def __iter__(self):
        return self

    def __next__(self):
        if self.sdi is None:
            raise StopIteration()
        result = None
        try:
            result = self.sdi.__next__()
        except StopIteration:
            for t in self.ts:
                if t.staticSize() != 0:
                    self.sdi = StaticDataIterator(t)
                    result = self.sdi.__next__()
                    break
        if result is None:
            raise StopIteration()
        return result
