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
    namespace: str = None,
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
class StringNode(ExprNode):
    literal: str = None


@dataclass
class AddNode(ExprNode):
    leftNode: ExprNode = None,
    rightNode: ExprNode = None


@dataclass
class MultNode(ExprNode):
    leftNode: ExprNode = None,
    rightNode: ExprNode = None


@dataclass
class SubNode(ExprNode):
    leftNode: ExprNode = None,
    rightNode: ExprNode = None


@dataclass
class DivNode(ExprNode):
    leftNode: ExprNode = None,
    rightNode: ExprNode = None
