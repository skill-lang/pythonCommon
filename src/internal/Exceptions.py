from src.internal.FieldDeclaration import FieldDeclaration
from src.internal.FieldType import FieldType
from src.streams.FileInputStream import FileInputStream


class InvalidPoolIndexException(Exception):

    def __init__(self, index, size, pool):
        self.message = str.format("Invalid index {} into pool {} of size {}", index, pool, size)


class PoolSizeMismatchError(Exception):

    def __init__(self, block, position, begin, end, field: FieldDeclaration):
        self.message = str.format("Corrupted data chunk in block {} between {} and {} in Field {} of type: {}", block + 1, begin, end, field.owner()) # TODO


class TypeMismatchError(Exception):

    def __init__(self, type: FieldType, expected: str, field: str, pool: str):
        self.message = str.format("During construction of {}.{}: Encountered incompatible type {} (expected: {})", pool, field, type.__str__(), expected)


class ParseException(Exception):

    def __init__(self, inStream: FileInputStream, block, cause, msgFormat, *msgArgs):
        self.message = str.format("In block {} {}: {}", block + 1, inStream.position(), str.format(msgFormat, msgArgs))


class SkillException(Exception):

    def __init__(self, msg: str, enableSuppression: bool, writableStackTrace: bool):
        super(SkillException, self).__init__(msg, enableSuppression, writableStackTrace)
