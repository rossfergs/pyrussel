from __future__ import annotations
from dataclasses import dataclass, field

from ParseNode import BlockNode

@dataclass
class Scope:
    current_scope: dict[str, BlockNode] = field(default_factory=dict)
    outer_scope: Scope = None
