import os
from common.streams.OutStream import OutStream
from typing import TypeVar
from io import BufferedWriter, BufferedRandom

W = TypeVar('W', BufferedWriter, BufferedRandom)


class FileOutputStream(OutStream):
    """
    Stream to write data to a file.
    """

    def __init__(self, file: W, position=0):
        super(FileOutputStream, self).__init__(file)
        self.pos = position

    @staticmethod
    def write(target):
        """
        Opens a file if necessary.
        :param target: file object
        :return: FileOutputStream
        """
        f: W = target.file
        if f.closed:
            f = open(target.path, 'rb+')  # ignore warning. Returned type is somehow fitting to what we expect.
        f.seek(0)
        return FileOutputStream(f)

    @staticmethod
    def append(target):
        """
        Opens the file if necessary and junps to the end.
        :param target: file object
        :return: FileOutputStream
        """
        f: W = target.file
        if f.closed:
            f = open(target.path, 'rb+')  # ignore warning. Returned type is somehow fitting to what we expect.
            return FileOutputStream(f)
        size = os.stat(target.path).st_size
        f.seek(size)
        return FileOutputStream(f, size)

    def flush(self):
        """
        Flush to the file.
        :return:
        """
        if self.file is not None:
            self.file.flush()

    def close(self):
        """
        Flush, truncatee and then close the file.
        :return:
        """
        if not self.file.closed:
            self.flush()
            self.file.truncate(self.file.tell())
            self.file.close()
