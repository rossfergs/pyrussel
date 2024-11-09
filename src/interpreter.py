from typing import Callable

from parser import parse
from error import Error, InterpreterError
from ParseNode import (
    ParseNode, ExprNode, AddNode,
    MultNode, SubNode, DivNode,
    IntegerNode, FloatNode, StringNode,
    PrintNode, LetNode, StatementNode,
    ProgramNode, VariableNode, BlockNode
)
from Scope import Scope
from Value import Value, IntValue, StringValue, FloatValue


def get_variable_value(name: str, scope: Scope) -> Value:
    if name not in scope.current_scope:
        if scope.outer_scope is None:
            InterpreterError(f"Unknown variable '{name}'")

        return get_variable_value(name, scope.outer_scope)

    return scope.current_scope[name]


def interpret_expression(node: ExprNode, scope: Scope) -> Value:

    def find_result_type(left_node: Value, right_node: Value) -> (str, Value, Value):
        match (left_node.var_type, right_node.var_type):
            case ("Int", "Int") | ("Float", "Float") | ("Str", "Str"):
                return left_node.var_type, left_node, right_node
            case ("Str", _) | (_, "Str"):
                InterpreterError(f"Type mismatch: {left_node.var_type} and {right_node.var_type}")
                return "Str", StringValue(left_node.value), StringValue(right_node.value)
            case ("Float", _) | (_, "Float"):
                return "Float", FloatValue(left_node.value), FloatValue(right_node.value)
            case ("Bool", _) | (_, "Bool"):
                InterpreterError("Cannot apply operations on boolean type")
            case _:
                Error("unknown result type from operation")

    def apply_binary_operator(
            left_node: ExprNode,
            right_node: ExprNode,
            operation: Callable[[Value, Value], Value]) -> Value:

        left_value = interpret_expression(left_node, scope)
        right_value = interpret_expression(right_node, scope)

        t, lv, rv = find_result_type(left_value, right_value)
        match t:
            case "Int":
                return IntValue(operation(lv.value, rv.value))
            case "Float":
                return FloatValue(operation(lv.value, rv.value))
            case "Str":
                return StringValue(operation(lv.value, rv.value))

    if isinstance(node, IntegerNode):
        return IntValue(int(node.value))

    if isinstance(node, StringNode):
        return StringValue(node.value)

    if isinstance(node, FloatNode):
        return FloatValue(node.value)

    if isinstance(node, VariableNode):
        return get_variable_value(node.namespace, scope)

    match node:
        case AddNode():
            return apply_binary_operator(node.left, node.right, lambda x, y: x + y)
        case MultNode():
            return apply_binary_operator(node.left, node.right, lambda x, y: x * y)
        case SubNode():
            return apply_binary_operator(node.left, node.right, lambda x, y: x - y)
        case _:
            Error("Unknown expression type")


def interpret_block(node: BlockNode, scope: Scope, statement_idx: int = 0) -> tuple[Value, Scope]:
    if statement_idx >= len(node.statements):
        return interpret_expression(node.expression, scope), scope.outer_scope

    scope = interpret_statement(node.statements[statement_idx], scope)

    return interpret_block(node, scope, statement_idx + 1)


def interpret_assignment(node: LetNode, scope: Scope) -> Scope:
    evaluated_expression, scope = interpret_block(node.expression, scope)
    scope.current_scope[node.namespace] = evaluated_expression
    return scope


def interpret_print(node: PrintNode, scope: Scope) -> None:
    evaluated_expression = interpret_expression(node.expression, scope)
    print(evaluated_expression.value)


def interpret_statement(node: StatementNode, scope: Scope) -> Scope:
    if isinstance(node, LetNode):
        inner_scope = Scope()
        inner_scope.outer_scope = scope
        new_scope = interpret_assignment(node, inner_scope)
        return new_scope

    if isinstance(node, PrintNode):
        interpret_print(node, scope)
        return scope

    if isinstance(node, ExprNode):
        v = interpret_expression(node, scope)
        print(v.value)
        return scope

    Error("Not yet implemented statement type")


def interpret_program(node: ProgramNode) -> None:

    def interpret_statements(statements: list[StatementNode], idx: int = 0, scope: Scope = Scope()) -> None:

        if idx >= len(statements):
            return None

        current_scope = interpret_statement(statements[idx], scope)

        return interpret_statements(statements, idx + 1, current_scope)

    interpret_statements(node.statements)


def interpret(input_string: str) -> None:
    tree = parse(input_string)
    if not isinstance(tree, ProgramNode):
        Error("Start node must be of type ProgramNode")

    interpret_program(tree)
