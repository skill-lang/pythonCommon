import os
from common.streams.InStream import InStream
from io import BufferedReader, BufferedRandom
from typing import TypeVar

R = TypeVar('R', BufferedReader, BufferedRandom)


class FileInputStream(InStream):
    """
    Stream to read from the file.
    """

    def __init__(self, file: R, path):
        super(FileInputStream, self).__init__(file)
        self.path = path
        self.storedPosition = None
        self.pos = 0

    @staticmethod
    def open(path):
        """
        Opens file in specified path.
        :param path: path to the file to open
        :return: FileInputStream
        """
        if not os.path.exists(path):
            open(path, "x").close()
        file: R = open(path, 'rb+', 4096)  # ignore warning. Returned type is somehow fitting to what we expect.
        return FileInputStream(file, path)

    def jump(self, position):
        """
        Jumps to specified position in the file.
        :param position: position in the file
        :return:
        """
        self.file.seek(position)

    def push(self, position):
        """
        Jump to position in the file and save current position.
        :param position: position in the file
        :return:
        """
        self.storedPosition = self.file.tell()
        self.file.seek(position)

    def pop(self):
        """
        Jump back to the stored position.
        :return:
        """
        if self.storedPosition is not None:
            self.file.seek(self.storedPosition)
        else:
            raise IOError("There is no FileInputStream.storedPosition")

    def close(self):
        """
        Close the stream.
        :return:
        """
        self.file.close()
