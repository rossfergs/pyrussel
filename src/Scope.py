from __future__ import annotations
from dataclasses import dataclass, field
from Value import Value


@dataclass
class Scope:
    current_scope: dict[str, Value] = field(default_factory=dict)
    outer_scope: Scope = None
