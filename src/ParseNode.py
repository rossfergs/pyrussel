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
class ExprNode(ParseNode):
    pass


@dataclass
class BlockNode(ExprNode):
    parameters: list[str] = field(default_factory=list)
    statements: list[StatementNode] = field(default_factory=list)
    expression: ExprNode = None


@dataclass
class VariableNode(ExprNode):
    namespace: str = None
    parameters: list[ExprNode] = None


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
