import abc
import os
from src.api.SkillFile import *
from src.streams.FileInputStream import FileInputStream
from src.internal.StringPool import StringPool
from src.internal.StoragePool import StoragePool
from src.internal.SkillObject import SkillObject
from src.internal.Exceptions import *
import traceback


class SkillState(abc.ABC, SkillFile):

    def __init__(self):
        self.isWindows = (os.name == 'nt')
        self.poolByName = {}
        self.writeMode = None
        self.path = None
        self.input: FileInputStream = None
        self.dirty = False
        self.strings: StringPool = None
        self.annotationType = None
        self.types = []
        self.pool = None

    def pool(self, name):
        return self.poolByName[name]

    def finalizePools(self, fis: FileInputStream):
        pass
        try:
            StoragePool.establishNextPool(self.types)
        except InterruptedError:
            traceback.print_exc()

    def String(self):
        return self.strings

    def contains(self, target: SkillObject):
        if target is None or target == 0:
            return True
        try:
            if target.skillId > 0:
                return target == self.poolByName[target.skillName()].getByID(target.skillId)
            return target in self.poolByName[target.skillName()].newObjects
        except:
            return False

    def delete(self, target: SkillObject):
        if target is not None:
            self.dirty = self.dirty | (target.skillId > 0)
            self.poolByName[target.skillName()].delete(target)

    def changePath(self, path):
        if self.writeMode == "append":
            if self.path == path:
                return
            # TODO Files
        elif self.writeMode == "readonly":
            self.writeMode = "write"
        else:
            return
        self.path = path

    def changeMode(self, writeMode: str):
        if self.writeMode == writeMode:
            return

        if writeMode == "write":
            self.writeMode = writeMode
        elif writeMode == "append":
            raise Exception("Cannot change write mode from write to append, "
                            "try to use open(path, 'create', 'append') instead.")
        elif writeMode == "readonly":
            raise Exception("Cannot change from read only to a write mode.")
        else:
            return

    def loadLazyData(self):
        id = len(self.strings.idMap)
        while id != 0:
            var = self.strings[0]
            id -= 1

        for p in self.types:
            for f in p.dataFields:
                # TODO ensureLoad if f isinstance of LazyField
                pass

    def check(self):
        for p in self.types:
            for f in p.dataFields:
                try:
                    f.check()
                except SkillException as e:
                    raise SkillException(format("check failed in [].[]:[]  []", p.name, f.name, 1, e)) # TODO e.getMessage instead of 1

    def flush(self):
        try:
            if self.writeMode == "write":
                if self.isWindows:
                    target = self.path
                    # TODO create File
                else:
                    # TODO new StateWriter
                    pass
                return
            elif self.writeMode == "append":
                if self.dirty:
                    self.changeMode("write")
                    self.flush()
                else:
                    pass
                    # TODO new StateAppender
                return
            elif self.writeMode == "readonly":
                raise SkillException("Cannot flush a read only file. Note: close will turn a file into read only.")
        except SkillException as e:
            raise e
        except IOError as e:
            raise SkillException("failed to create or complete out stream", e)
        except Exception as e:
            raise SkillException("unexpected exception", e)

    def _makeInStream_(self):
        if self.input is None or not (self.path == self.input.path):
            self.input = FileInputStream(self.path, False)
        return self.input

    def close(self):
        if self.writeMode != "readonly":
            self.flush()
            self.writeMode = "readonly"

        if self.input is not None:
            try:
                self.input.close()
            except IOError:
                traceback.print_exc()
