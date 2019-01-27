from src.internal.FieldDeclaration import FieldDeclaration
from src.internal.FieldType import FieldType
from src.streams.FileInputStream import FileInputStream


class InvalidPoolIndexException(Exception):

    def __init__(self, index, size, pool, cause=None):
        super(InvalidPoolIndexException, self).__init__(index, size, pool, cause)
        self.message = str.format("Invalid index {} into pool {} of size {}", index, pool, size)


class PoolSizeMismatchError(Exception):

    def __init__(self, block, begin, end, field: FieldDeclaration, position=-1):
        if position != -1:
            super(PoolSizeMismatchError, self).__init__(
                "Corrupted data chunk in block {} at {} between {} and {} in Field {}.{} of type: {}",
                block + 1, position, begin, end, field.owner.name, field.name, field.fType.toString())
        else:
            super(PoolSizeMismatchError, self).__init__(
                "Corrupted data chunk in block {} between {} and {} in Field {}.{} of type: {}",
                block + 1, begin, end, field.owner.name, field.name, field.fType.toString())


class TypeMismatchError(Exception):

    def __init__(self, fType: FieldType, expected: str, field: str, pool: str):
        super(TypeMismatchError, self).__init__(
            "During construction of {}.{}: Encountered incompatible type {} (expected: {})",
            pool, field, fType.toString(), expected)


class ParseException(Exception):

    def __init__(self, inStream, block, cause, msgFormat, *msgArgs):
        super(ParseException, self).__init__("In block {} {}: {}".format(block + 1, inStream.position(),
                                                                         msgFormat.format(msgArgs)), cause)


class SkillException(Exception):

    def __init__(self, msg=None, cause=None):
        super(SkillException, self).__init__(msg, cause)
        self.message = msg
