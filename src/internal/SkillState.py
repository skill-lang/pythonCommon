import os
import shutil
import tempfile
from src.api.SkillFile import *
from src.internal.BasePool import BasePool
from src.internal.LazyField import LazyField
from src.internal.StateAppender import StateAppender
from src.internal.StateWriter import StateWriter
from src.internal.StringPool import StringPool
from src.internal.StoragePool import StoragePool
from src.internal.SkillObject import SkillObject
from src.internal.fieldTypes.Annotation import Annotation
from src.internal.Exceptions import *
import traceback
from concurrent.futures import ThreadPoolExecutor
from threading import Semaphore
from src.streams.FileOutputStream import FileOutputStream


class SkillState(abc.ABC, SkillFile):

    isWindows = (os.name == 'nt')
    threadPool = ThreadPoolExecutor()

    def __init__(self, strings: StringPool, path, mode: SkillFile.Mode, types: [],
                 poolByName: {}, annotationType: Annotation):
        self.strings: StringPool = strings
        self.path = path
        self.writeMode: SkillFile.Mode = mode
        self.types = types
        self.poolByName = poolByName
        self.annotationType = annotationType

        self.input: FileInputStream = strings.inStream
        self.dirty = False

    def finalizePools(self, fis: FileInputStream):
        try:
            StoragePool.establishNextPool(self.types)

            barrier = Semaphore(0)
            reads = 0
            fieldNames = set()
            for p in self.allTypes():
                if isinstance(p, BasePool):
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

    def String(self):
        return self.strings

    def contains(self, target: SkillObject):
        if target is None or target == 0:
            return True
        try:
            if target.skillID > 0:
                return target == self.poolByName[target.skillName()].getByID(target.skillID)
            return target in self.poolByName[target.skillName()].newObjects
        except Exception:
            return False

    def delete(self, target: SkillObject):
        if target is not None:
            self.dirty = self.dirty | (target.skillID > 0)
            self.poolByName[target.skillName()].delete(target)

    def changePath(self, path):
        if self.writeMode == SkillFile.Mode.Append:
            if self.path == path:
                return
            if os.path.exists(path):
                os.remove(path)
            shutil.copy2(self.path, path)
        elif self.writeMode == SkillFile.Mode.ReadOnly:
            self.writeMode = SkillFile.Mode.Write
        else:
            return
        self.path = path

    def changeMode(self, writeMode):
        if self.writeMode == writeMode:
            return

        if writeMode == SkillFile.Mode.Write:
            self.writeMode = writeMode
        elif writeMode == SkillFile.Mode.Append:
            raise Exception("Cannot change write mode from write to append, "
                            "try to use open(path, 'create', 'append') instead.")
        elif writeMode == SkillFile.Mode.ReadOnly:
            raise Exception("Cannot change from read only to a write mode.")
        else:
            return

    def loadLazyData(self):
        ID = len(self.strings.idMap)
        while ID != 0:
            var = self.strings[0]
            ID -= 1

        for p in self.types:
            for f in p.dataFields:
                if isinstance(f, LazyField):
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
            if self.writeMode == SkillFile.Mode.Write:
                if self.isWindows:
                    target = self.path
                    with tempfile.TemporaryDirectory(None, "temp", ".") as d:
                        f = tempfile.TemporaryFile('w+b', -1, None, None, ".sf", "write", d)
                    self.changePath(os.path.join(d, f))
                    StateWriter(self, FileOutputStream.write(self.makeInStream()))
                    # TODO create File
                else:
                    StateWriter(self, FileOutputStream.write(self.makeInStream()))
                return
            elif self.writeMode == SkillFile.Mode.Append:
                if self.dirty:
                    self.changeMode(SkillFile.Mode.Write)
                    self.flush()
                else:
                    StateAppender(self, FileOutputStream.append(self.makeInStream()))
                return
            elif self.writeMode == "readonly":
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
        if self.writeMode != "readonly":
            self.flush()
            self.writeMode = "readonly"

        if self.input is not None:
            try:
                self.input.close()
            except IOError:
                traceback.print_exc()
