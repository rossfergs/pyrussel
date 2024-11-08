from __future__ import annotations
from dataclasses import dataclass, field
from Variable import Variable


@dataclass
class Scope:
    current_scope: dict[str, Variable] = field(default_factory=dict)
    outer_scope: Scope = None
