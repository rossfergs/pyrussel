from __future__ import annotations
from dataclasses import dataclass
from typing import Any

from ParseNodeType import ParseNodeTypes


@dataclass
class ParseNode:
    type: ParseNodeTypes = None
    value: str = None
    operator: str = None
    statements: list[ParseNode] = None
