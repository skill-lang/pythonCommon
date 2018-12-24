from src.streams import FileInputStream


class StringPool:

    def __init__(self, inStream: FileInputStream):
        self.inStream = inStream
        self.stringPositions = []
        self.idMap = []

    def get(self, index):
        if index is 0: return None

        try:
            result = self.idMap[index]
        except IndexError:
            raise

    class Position:

        def __init__(self, l, i):
            self.absolutOffset = l
            self.length = i
