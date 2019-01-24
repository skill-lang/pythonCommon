

class Block:

    def __init__(self, bpo, count, staticCount):
        self.bpo = bpo
        self.count = count
        self.staticCount = staticCount

    def contains(self, skillID):
        return self.bpo < skillID & skillID <= self.bpo + self.count


class Chunk:

    def __init__(self, begin, end, count):
        self.begin = begin
        self.end = end
        self.count = count


class BulkChunk(Chunk):

    def __init__(self, begin, end, count, blockCount):
        super(BulkChunk, self).__init__(begin, end, count)
        self.blockCount = blockCount


class SimpleChunk(Chunk):

    def __init__(self, begin, end, bpo, count):
        super(SimpleChunk, self).__init__(begin, end, count)
        self.bpo = bpo
