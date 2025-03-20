from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ParseNode:
    pass


@dataclass
class ProgramNode(ParseNode):
    statements: list[StatementNode]


@dataclass
class StatementNode(ParseNode):
    pass


@dataclass
class LetNode(StatementNode):
    namespace: VariableNode = None,
    block: BlockNode = None


@dataclass
class PrintNode(StatementNode):
    expression: ExprNode = None


@dataclass
class PrintLnNode(StatementNode):
    expression: ExprNode = None


@dataclass
class ExprNode(ParseNode):
    pass


@dataclass
class IfNode(ExprNode):
    condition: ExprNode
    then_block: ExprNode
    else_block: ExprNode


@dataclass
class BlockNode(ExprNode):
    parameters: list[str] = field(default_factory=list)
    statements: list[StatementNode] = field(default_factory=list)
    expression: ExprNode = None,
    lexical_scope: tuple[list] = None


@dataclass
class VariableNode(ExprNode):
    namespace: str = None
    parameters: list[ExprNode] = None


@dataclass
class BoolNode(ExprNode):
    value: bool = None


@dataclass
class IntegerNode(ExprNode):
    value: int = None


@dataclass
class FloatNode(ExprNode):
    value: float = None


@dataclass
class StringNode(ExprNode):
    value: str = None


@dataclass
class EqNode(ExprNode):
    left: ExprNode = None,
    right: ExprNode = None


@dataclass
class NeqNode(ExprNode):
    left: ExprNode = None,
    right: ExprNode = None


@dataclass
class GeqNode(ExprNode):
    left: ExprNode = None,
    right: ExprNode = None


@dataclass
class LeqNode(ExprNode):
    left: ExprNode = None,
    right: ExprNode = None


@dataclass
class GreaterNode(ExprNode):
    left: ExprNode = None,
    right: ExprNode = None


@dataclass
class LessNode(ExprNode):
    left: ExprNode = None,
    right: ExprNode = None


@dataclass
class AddNode(ExprNode):
    left: ExprNode = None,
    right: ExprNode = None


@dataclass
class MultNode(ExprNode):
    left: ExprNode = None,
    right: ExprNode = None


@dataclass
class SubNode(ExprNode):
    left: ExprNode = None,
    right: ExprNode = None


@dataclass
class DivNode(ExprNode):
    left: ExprNode = None,
    right: ExprNode = None


@dataclass
class ListNode(ExprNode):
    data: ExprNode = None,
    next: ExprNode = None


@dataclass
class NilNode(ExprNode):
    pass


@dataclass
class ConsNode(ExprNode):
    left: ExprNode = None,
    right: ExprNode = None


@dataclass
class MatchNode(ExprNode):
    expr: ExprNode = None
    cases: list[ExprNode] = field(default_factory=list)


@dataclass
class CaseNode(ExprNode):
    pattern: ExprNode = None,
    guard: ExprNode = None,
    block: BlockNode = None


@dataclass
class TaggedNode(ExprNode):
    tag: str = None
    expression: ExprNode = None


@dataclass
class ImportNode(StatementNode):
    file_path: str = None


@dataclass
class NegativeNode(ExprNode):
    expression: ExprNode = None
