import abc


class Block:
    """
    A block contains information about instances in a type. A StoragePool holds blocks in order of appearance
    in a file with the invariant, that the latest block in the list will be the latest block in the file.
    If a StoragePool holds no block, then it has no instances in a file.
    Note: While writing a Pool to disk, the latest block is the block currently written.
    """

    def __init__(self, bpo, count, staticCount):
        """
        :param bpo: the offset of the first instance
        :param count: the number of instances in this chunk
        :param staticCount
        """
        self.bpo = bpo
        self.count = count
        self.staticCount = staticCount

    def contains(self, skillID: int) -> bool:
        """
        :return: true, if the object with the argument SkillID is inside this block
        """
        return self.bpo < skillID & skillID <= self.bpo + self.count


class Chunk(abc.ABC):
    """
    Chunks contain information on where field data can be found.
    Note: indices of recipient of the field data is not necessarily continuous; make use of staticInstances!
    Note: begin and end are mutable, because they will contain relative offsets while parsing a type block
    Note: this is a POJO that shall not be passed to users!
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
        super(BulkChunk, self).__init__(begin, end, count)
        self.blockCount = blockCount  # number of blocks represented by this chunk


class SimpleChunk(Chunk):
    """
    A chunk used for regular appearances of fields.
    """

    def __init__(self, begin, end, bpo, count):
        super(SimpleChunk, self).__init__(begin, end, count)
        self.bpo = bpo
