import os
import shutil
import tempfile
from src.internal.StateAppender import StateAppender
from src.internal.StateWriter import StateWriter
from src.internal.StoragePool import StoragePool
from src.internal.Exceptions import SkillException
from src.internal.Mode import Mode
import traceback
from threading import Semaphore
from src.streams.FileOutputStream import FileOutputStream
from src.streams.FileInputStream import FileInputStream


class SkillState:

    isWindows = (os.name == 'nt')

    def __init__(self, strings, path, mode: Mode, types: [],
                 poolByName: {}, annotationType):
        self.strings = strings
        self.path = path
        self.writeMode: Mode = mode
        self.types = types
        self.poolByName = poolByName
        self.annotationType = annotationType

        self.input = strings.inStream
        self.dirty = False

    def finalizePools(self, fis):
        try:
            StoragePool.establishNextPool(self.types)

            barrier = Semaphore(0)
            reads = 0
            fieldNames = set()
            for p in self.allTypes():
                if p.owner is None:  # if p is BasePool
                    p.owner = self
                    reads += p.performAllocations(barrier)
                # add missing field declarations
                fieldNames.clear()
                for f in p.dataFields:
                    fieldNames.add(f.name)
                # ensure existence of known fields
                for n in p.knownFields:
                    if n not in fieldNames:
                        p.addKnownField(n, self.strings, self.annotationType)
            for _ in range(reads):
                barrier.acquire()

            # read field data
            reads = 0
            readErrors = []
            for p in self.allTypes():
                for f in p.dataFields:
                    reads += f.finish(barrier, readErrors, fis)

            self.annotationType.fixTypes(self.poolByName)
            for _ in range(reads):
                barrier.acquire()
            for e in readErrors:
                raise e
            if not len(readErrors) == 0:
                raise readErrors[0]
        except InterruptedError:
            traceback.print_exc()

    def Strings(self):
        return self.strings

    def contains(self, target):
        if target is None or target == 0:
            return True
        try:
            if target.skillID > 0:
                return target == self.poolByName[target.skillName()].getByID(target.skillID)
            return target in self.poolByName[target.skillName()].newObjects
        except Exception:
            return False

    def delete(self, target):
        if target is not None:
            self.dirty = self.dirty | (target.skillID > 0)
            self.poolByName[target.skillName()].delete(target)

    def changePath(self, path):
        if self.writeMode == Mode.Append:
            if self.path == path:
                return
            if os.path.exists(path):
                os.remove(path)
            shutil.copy2(self.path, path)
        elif self.writeMode == Mode.ReadOnly:
            self.writeMode = Mode.Write
        else:
            return
        self.path = path

    def changeMode(self, writeMode):
        if self.writeMode == writeMode:
            return

        if writeMode == Mode.Write:
            self.writeMode = writeMode
        elif writeMode == Mode.Append:
            raise Exception("Cannot change write mode from write to append, "
                            "try to use open(path, Create, Append) instead.")
        elif writeMode == Mode.ReadOnly:
            raise Exception("Cannot change from read only to a write mode.")
        else:
            return

    def loadLazyData(self):
        for ID in range(0, len(self.strings.idMap)):
            self.strings.get(ID)
            ID -= 1
        for p in self.types:
            for f in p.dataFields:
                if f.isLazy:
                    f.ensureLoaded()

    def check(self):
        for p in self.types:
            for f in p.dataFields:
                try:
                    f.check()
                except SkillException as e:
                    raise SkillException("check failed in [].[]:\n []".format(
                        p.name, f.name, e.message), e)

    def flush(self):
        try:
            if self.writeMode == Mode.Write:
                if self.isWindows:
                    target = self.path
                    f = tempfile.TemporaryFile('w+b', -1, None, None, ".sf", "write")
                    self.changePath(f.name)
                    StateWriter(self, FileOutputStream.write(self.makeInStream()))
                    f.name = target
                    self.changePath(target)
                else:
                    StateWriter(self, FileOutputStream.write(self.makeInStream()))
                return
            elif self.writeMode == Mode.Append:
                if self.dirty:
                    self.changeMode(Mode.Write)
                    self.flush()
                else:
                    StateAppender(self, FileOutputStream.append(self.makeInStream()))
                return
            elif self.writeMode == Mode.ReadOnly:
                raise SkillException("Cannot flush a read only file. Note: close will turn a file into read only.")
        except SkillException as e:
            raise e
        except IOError as e:
            raise SkillException("failed to create or complete out stream", e)
        except Exception as e:
            raise SkillException("unexpected exception", e)

    def makeInStream(self):
        if self.input is None or not (self.path == self.input.path):
            self.input = FileInputStream.open(self.path, False)
        return self.input

    def close(self):
        if self.writeMode != Mode.ReadOnly:
            self.flush()
            self.writeMode = Mode.ReadOnly

        if self.input is not None:
            try:
                self.input.close()
            except IOError:
                traceback.print_exc()

    def currentPath(self):
        return self.path
