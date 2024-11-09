from dataclasses import dataclass
from TokenType import TokenType


@dataclass(frozen=True)
class Token:
    type: TokenType
    literal: str
