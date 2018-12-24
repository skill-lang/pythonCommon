from src.internal.FieldType import FieldType


class Annotation(FieldType):

    def __init__(self, types):
        self.types = types
