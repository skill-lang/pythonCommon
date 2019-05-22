import os
import shutil
import tempfile
from common.internal.StateAppender import StateAppender
from common.internal.StateWriter import StateWriter
from common.internal.StoragePool import StoragePool
from common.internal.Exceptions import SkillException
from common.internal.Mode import Mode
import traceback
from common.streams.FileOutputStream import FileOutputStream
from common.streams.FileInputStream import FileInputStream
from common.internal.BasePool import BasePool


class SkillState:
    """
    SkillFile representation in memory. Holds all information of a binary file.
    """

    isWindows = (os.name == 'nt')

    def __init__(self, strings, path, mode: Mode, types: [],
                 poolByName: {}, annotationType):
        self._strings = strings
        self.__path = path
        self.__writeMode: Mode = mode
        self.__types = types
        self._poolByName = poolByName
        self.__annotationType = annotationType

        self.__input = strings.inStream
        self.__dirty = False

    def _finalizePools(self, fis):
        """
        Finalize reading a binary file.
        :param fis: FileInputStream
        :return:
        """
        try:
            StoragePool._establishNextPool(self.__types)

            fieldNames = set()
            for p in self.allTypes():
                if isinstance(p, BasePool):  # if p is BasePool
                    p._owner = self
                    p._performAllocations()
                # add missing field declarations
                fieldNames.clear()
                for f in p._dataFields:
                    fieldNames.add(f.name())
                # ensure existence of known fields
                for n in p.knownFields:
                    if n not in fieldNames:
                        p.addKnownField(n, self._strings, self.__annotationType)

            # read field data
            readErrors = []
            for p in self.allTypes():
                for f in p._dataFields:
                    f._finish(readErrors, fis)

            self.__annotationType.fixTypes(self._poolByName)
            for e in readErrors:
                raise e
            if not len(readErrors) == 0:
                raise readErrors[0]
        except InterruptedError:
            traceback.print_exc()

    def Strings(self):
        """
        :return: StringPool of this SkillState
        """
        return self._strings

    def contains(self, target):
        """
        Holds this SkillState target?
        :param target: SkillObject
        :return: True if SkillState holds this instance or target is None or deleted
        """
        if target is None or target.skillID == 0:
            return True
        try:
            if target.skillID > 0:
                return target == self._poolByName[target.skillName()].getByID(target.skillID)
            return target in self._poolByName[target.skillName()].newObjects
        except Exception:
            return False

    def delete(self, target):
        """
        Delete instance by setting skillID to 0
        :param target: SkillObject
        :return:
        """
        if target is not None:
            self.__dirty = self.__dirty | (target.skillID > 0)
            self._poolByName[target.skillName].delete(target)

    def changePath(self, path):
        """
        Change path of the binary file.
        :param path: new path
        :return:
        """
        if self.__writeMode == Mode.Write:
            self.__path = path
            return
        elif self.__writeMode == Mode.Append:
            if self.__path == path:
                return
            if os.path.exists(path):
                os.remove(path)
            shutil.copy2(self.__path, path)
        elif self.__writeMode == Mode.ReadOnly:
            self.__writeMode = Mode.Write
        else:
            return
        self.__path = path

    def changeMode(self, writeMode):
        """
        Change write mode
        :param writeMode: new write mode
        :return:
        """
        if self.__writeMode == writeMode:
            return

        if writeMode == Mode.Write:
            self.__writeMode = writeMode
        elif writeMode == Mode.Append:
            raise Exception("Cannot change write mode from write to append, "
                            "try to use open(path, Create, Append) instead.")
        elif writeMode == Mode.ReadOnly:
            raise Exception("Cannot change from read only to a write mode.")
        else:
            return

    def loadLazyData(self):
        """
        Load all lazy loaded data.
        :return:
        """
        for ID in range(0, len(self._strings.idMap)):
            self._strings.get(ID)
        for p in self.__types:
            for f in p._dataFields:
                if f.isLazy:
                    f._ensureLoaded()

    def flush(self):
        """
        Flush to the binary file.
        :return:
        """
        try:
            if self.__writeMode == Mode.Write:
                if self.isWindows:
                    target = self.__path
                    f = tempfile.TemporaryFile('w+b', -1, None, None, ".sf", "write")
                    self.changePath(f.name)
                    StateWriter(self, FileOutputStream.write(self.__makeInStream()))
                    f._name = target
                    self.changePath(target)
                else:
                    StateWriter(self, FileOutputStream.write(self.__makeInStream()))
                return
            elif self.__writeMode == Mode.Append:
                if self.__dirty:
                    self.changeMode(Mode.Write)
                    self.flush()
                else:
                    StateAppender(self, FileOutputStream.append(self.__makeInStream()))
                return
            elif self.__writeMode == Mode.ReadOnly:
                raise SkillException("Cannot flush a read only file. Note: close will turn a file into read only.")
        except SkillException as e:
            raise e
        except IOError as e:
            raise SkillException("failed to create or complete out stream", e)
        except Exception as e:
            raise SkillException("unexpected exception", e)

    def __makeInStream(self):
        """
        If FileInputStream is closed or None, a new FileInputStream will be opened.
        :return: current FileInputStream
        """
        if self.__input is None or self.__input.file.closed or not (self.__path == self.__input.path):
            self.__input = FileInputStream.open(self.__path)
        return self.__input

    def close(self):
        """
        Flush and close the binary file. The SKillState will not be deleted.
        :return:
        """
        if self.__writeMode != Mode.ReadOnly:
            self.flush()
            self.__writeMode = Mode.ReadOnly

        if self.__input is not None:
            try:
                self.__input.close()
            except IOError:
                traceback.print_exc()

    def currentPath(self):
        """
        :return: current path of the binary file.
        """
        return self.__path

    def allTypes(self):
        """
        :return: list of all StoragePools in the SkillState
        """
        return self.__types
