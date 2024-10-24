import enum
from enum import Enum


class TokenType(Enum):
    OPAR = enum.auto()
    CPAR = enum.auto()
    ASS = enum.auto()
    FOR = enum.auto()
    ADD = enum.auto()
    MULT = enum.auto()
    SUB = enum.auto()
    DLM = enum.auto()
    PRINT = enum.auto()
    NAMESPACE = enum.auto()
    STRING = enum.auto()
    NUMBER = enum.auto()
