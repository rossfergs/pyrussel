import enum


class ParseNodeTypes(enum.Enum):
    NUMBER = enum.auto()
    STRING = enum.auto()
    NAMESPACE = enum.auto()
