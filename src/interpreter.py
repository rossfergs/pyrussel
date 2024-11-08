from error import Error
from ParseNode import (
    ParseNode, ExprNode, AddNode,
    MultNode, SubNode, DivNode,
    IntegerNode, VariableNode, StringNode,
    PrintNode, LetNode, StatementNode,
    ProgramNode
)
from Scope import Scope
from Variable import IntVariable


# TODO: Change this to work with non int types
# Figure out how to return values and such
def interpret_expression(node: ExprNode, scope: Scope) -> int:

    if isinstance(node, IntegerNode):
        return int(node.value)

    if isinstance(node, VariableNode):
        return scope.current_scope[node.namespace].value

    match node:
        case AddNode():
            return interpret_expression(node.leftNode, scope) + interpret_expression(node.rightNode, scope)
        case MultNode():
            return interpret_expression(node.leftNode, scope) * interpret_expression(node.rightNode, scope)
        case SubNode():
            return interpret_expression(node.leftNode, scope) - interpret_expression(node.rightNode, scope)
        case _:
            Error("Unknown expression type")


def interpret_assignment(node: LetNode, scope: Scope) -> Scope:
    evaluated_expression = interpret_expression(node.expression, scope)
    scope.current_scope[node.namespace] = IntVariable(evaluated_expression)
    return scope


def interpret_print(node: PrintNode, scope: Scope) -> None:
    evaluated_expression = interpret_expression(node.expression, scope)
    print(evaluated_expression)


def interpret_statement(node: StatementNode, scope: Scope) -> Scope:
    if isinstance(node, LetNode):
        new_scope = interpret_assignment(node, scope)
        return new_scope

    if isinstance(node, PrintNode):
        interpret_print(node, scope)
        return scope

    if isinstance(node, ExprNode):
        print(interpret_expression(node, scope))
        return scope

    Error("Not yet implemented statement type")


def interpret_program(node: ProgramNode) -> None:

    def interpret_statements(statements: list[StatementNode], idx: int = 0, scope: Scope = Scope()) -> None:

        if idx >= len(statements):
            return None

        current_scope = interpret_statement(statements[idx], scope)

        return interpret_statements(statements, idx + 1, current_scope)

    interpret_statements(node.statements)


def interpret(start_node: ParseNode) -> None:
    if not isinstance(start_node, ProgramNode):
        Error("Start node must be of type ProgramNode")

    interpret_program(start_node)
