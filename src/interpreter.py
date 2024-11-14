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


def get_from_scope(name: str, scope: Scope) -> ExprNode | BlockNode:
    if name not in scope.current_scope:
        if scope.outer_scope is None:
            InterpreterError(f"Unknown variable '{name}'")
        return get_from_scope(name, scope.outer_scope)

    return scope.current_scope[name]


def interpret_function(var: VariableNode, scope: Scope) -> ExprNode:

    def set_params(
            f_name: str,
            pl: list[str],
            al: list[ExprNode],
            idx: int = 0,
            sd: dict[str, ExprNode | BlockNode] = None) -> dict[str, ExprNode | BlockNode]:

        if sd is None:
            sd = {}

        if idx >= len(pl) and idx >= len(al):
            return sd

        if idx >= len(pl) or idx >= len(al):
            InterpreterError(f"function {f_name} takes in {len(pl)} parameters, but {len(al)} were given")

        if not isinstance(al[idx], VariableNode):
            new_block = BlockNode()
            new_block.expression = al[idx]
            sd[pl[idx]] = new_block
            return set_params(f_name, pl, al, idx + 1, sd)

        val = get_from_scope(al[idx].namespace, scope)
        if not isinstance(val, BlockNode):
            sd[pl[idx]] = val
            return set_params(f_name, pl, al, idx + 1, sd)

        if val.parameters and not al[idx].parameters:
            sd[pl[idx]] = val
            return set_params(f_name, pl, al, idx + 1, sd)

        block = BlockNode()
        block.expression = interpret_expression(al[idx], scope)
        sd[pl[idx]] = block

        return set_params(f_name, pl, al, idx + 1, sd)
    print(get_from_scope(var.namespace, scope).parameters)
    print(scope.current_scope[var.namespace].parameters)
    new_scope = Scope()
    new_scope.outer_scope = scope.current_scope
    new_scope.current_scope = set_params(var.namespace, get_from_scope(var.namespace, scope).parameters, var.parameters)

    result, result_scope = interpret_block(get_from_scope(var.namespace, scope), new_scope)
    return result


def interpret_expression(node: ExprNode, scope: Scope) -> ExprNode:

    def get_type(n: ExprNode) -> str:
        match n:
            case _ if isinstance(n, StringNode):
                return "Str"
            case _ if isinstance(n, IntegerNode):
                return "Int"
            case _ if isinstance(n, FloatNode):
                return "Float"
            case _:
                InterpreterError(f"Invalid Expression to get type from {n}")

    def find_result_type(l: ExprNode, r: ExprNode) -> tuple[str, ExprNode, ExprNode]:
        lt = get_type(l)
        rt = get_type(r)
        match (lt, rt):
            case ("Int", "Int") | ("Float", "Float") | ("Str", "Str"):
                return lt, l, r
            case ("Str", _) | (_, "Str"):
                InterpreterError(f"Type mismatch: {lt} and {rt}")
                return "Str", StringNode(l.value), StringNode(r.value)
            case ("Float", _) | (_, "Float"):
                return "Float", FloatNode(l.value), FloatNode(r.value)
            case ("Bool", _) | (_, "Bool"):
                InterpreterError("Cannot apply operations on boolean type")
            case _:
                Error("unknown result type from operation")

    def apply_binary_operator(
            left_node: ExprNode,
            right_node: ExprNode,
            operation: Callable[[ExprNode, ExprNode], ExprNode]) -> ExprNode:

        left_value = interpret_expression(left_node, scope)
        right_value = interpret_expression(right_node, scope)
        t, lv, rv = find_result_type(left_value, right_value)
        match t:
            case "Int":
                return IntegerNode(operation(lv.value, rv.value))
            case "Float":
                return FloatNode(operation(lv.value, rv.value))
            case "Str":
                return StringNode(operation(lv.value, rv.value))

    if isinstance(node, VariableNode):
        return interpret_function(node, scope)

    match node:
        case AddNode():
            return apply_binary_operator(node.left, node.right, lambda x, y: x + y)
        case MultNode():
            return apply_binary_operator(node.left, node.right, lambda x, y: x * y)
        case SubNode():
            return apply_binary_operator(node.left, node.right, lambda x, y: x - y)
        case IntegerNode() | StringNode() | FloatNode():
            return node
        case _:
            Error("Unknown expression type")


def interpret_block(node: BlockNode, scope: Scope, statement_idx: int = 0) -> tuple[ExprNode, Scope]:
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
        scope.current_scope[node.namespace] = node.block
        new_scope = scope
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
