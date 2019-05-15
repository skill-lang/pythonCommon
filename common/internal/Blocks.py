
class Block:
    """
    A block contains information about instances of a class. A StoragePool holds blocks in order of appearance
    in a file with the invariant, that the latest block in the list will be in the latest block in the file.
    If a StoragePool holds no block, then it has no instances in a file.
    """

    def __init__(self, bpo, count, staticCount):
        """
        :param bpo: the offset of the first instance
        :param count: the number of instances in this block
        :param staticCount
        """
        self.bpo = bpo
        self.count = count
        self.staticCount = staticCount

    def contains(self, skillID: int) -> bool:
        """
        :return: True, iff the object with the argument SkillID is inside this block, else False
        """
        return self.bpo < skillID & skillID <= self.bpo + self.count


class Chunk:
    """
    Chunks contain information on where field data can be found.
    Note: begin and end are mutable, because they will contain relative offsets while parsing a type block
    Note: should not be used by users!
    """

    def __init__(self, begin, end, count):
        """
        :param begin: position of the first byte of the first instance's data
        :param end: position of the last byte, i.e. the first byte that is not read
        :param count: the number of instances in this chunk
        """
        self.begin = begin
        self.end = end
        self.count = count


class BulkChunk(Chunk):
    """
    A chunk that is used iff a field is appended to a preexisting type in a block.
    """

    def __init__(self, begin, end, count, blockCount):
        """
        :param begin: position of the first byte of the first instance's data
        :param end: position of the last byte, i.e. the first byte that is not read
        :param count: the number of instances in this chunk
        :param blockCount: number of blocks represented by this chunk
        """
        super(BulkChunk, self).__init__(begin, end, count)
        self.blockCount = blockCount


class SimpleChunk(Chunk):
    """
    A chunk used for regular appearances of fields.
    """

    def __init__(self, begin, end, bpo, count):
        """
        :param begin: position of the first byte of the first instance's data
        :param end: position of the last byte, i.e. the first byte that is not read
        :param bpo: the offset of the first instance
        :param count: the number of instances in this chunk
        """
        super(SimpleChunk, self).__init__(begin, end, count)
        self.bpo = bpo
