from __future__ import annotations
from dataclasses import dataclass


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
    expression: ExprNode = None


@dataclass
class PrintNode(StatementNode):
    expression: ExprNode = None


@dataclass
class ExprNode(ParseNode):
    pass


@dataclass
class VariableNode(ExprNode):
    namespace: str = None


@dataclass
class IntegerNode(ExprNode):
    value: str = None


@dataclass
class FloatNode(ExprNode):
    value: str = None


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
