from typing import Callable
import copy

from parser import parse
from error import Error, InterpreterError
from ParseNode import (
    ExprNode, AddNode, PrintLnNode, NilNode,
    MultNode, SubNode, BoolNode, ConsNode,
    IntegerNode, FloatNode, StringNode,
    PrintNode, LetNode, StatementNode,
    ProgramNode, VariableNode, BlockNode,
    EqNode, NeqNode, GeqNode, LeqNode,
    LessNode, GreaterNode, IfNode, ListNode,
    MatchNode, CaseNode, TaggedNode, ImportNode,
    NegativeNode, DivNode
)
from Scope import Scope
import sys
sys.setrecursionlimit(5000)


def get_from_scope(name: str, scope: Scope) -> ExprNode | BlockNode:
    if name not in scope.current_scope:
        if scope.outer_scope is None:
            InterpreterError(f"Unknown variable '{name}'")
        return get_from_scope(name, scope.outer_scope)
    return scope.current_scope[name]


def match_list(pattern_list, expr_list, scope):
    match pattern_list, expr_list:
        case NilNode(), NilNode():
            return scope
        case ListNode(data=VariableNode(namespace="_"), next=pat_rem), ListNode(_, next=expr_rem):
            return match_list(pat_rem, expr_rem, scope)
        case ListNode(data=VariableNode(namespace=name), next=pat_rem), ListNode(data=data, next=expr_rem):
            new_scope = scope
            new_block = BlockNode(
                statements=[], expression=interpret_expression(data, scope), parameters=[])
            new_scope.current_scope[name] = new_block
            return match_list(pat_rem, expr_rem, new_scope)
        case ListNode(data=ListNode(), next=pat_rem), ListNode(data=ListNode(), next=expr_rem):
            match match_list(pattern_list.data, expr_list.data, scope):
                case None:
                    return None
                case new_scope:
                    return match_list(pat_rem, expr_rem, new_scope)
        case ListNode(data=ConsNode(), next=pat_rem), ListNode(data=ListNode(), next=expr_rem):
            match match_cons(expr_list.data, pattern_list.data.left, pattern_list.data.right, scope):
                case None:
                    return None
                case new_scope:
                    return match_list(pat_rem, expr_rem, new_scope)
        case ListNode(data=pat_data, next=pat_rem), ListNode(data=expr_data, next=expr_rem)\
                if interpret_expression(pat_data, scope) == interpret_expression(expr_data, scope):
            return match_list(pat_rem, expr_rem, scope)
        case _:
            return None


def match_tag(expr, pattern, scope) -> Scope | None:
    match pattern, expr:
        case TaggedNode(tag, VariableNode("_", _)), TaggedNode() if tag == expr.tag:
            return scope
        case TaggedNode(tag, VariableNode(namespace, _)), TaggedNode() if tag == expr.tag:
            new_block = BlockNode(
                statements=[], expression=interpret_expression(expr.expression, scope))
            new_scope = scope
            new_scope.current_scope[namespace] = new_block
            return new_scope
        case TaggedNode(pat_tag, TaggedNode()), TaggedNode(expr_tag, TaggedNode()) if tag == expr.tag:
            return match_tag(expr.expression, pattern.expression, scope)
        case TaggedNode(tag, NilNode()), TaggedNode(_, NilNode()) if tag == expr.tag:
            return scope
        case TaggedNode(tag, ListNode()), TaggedNode(_, ListNode()) if tag == expr.tag:
            return match_list(pattern.expression, expr.expression, scope)
        case TaggedNode(tag, ConsNode()), TaggedNode(_, ListNode()) if tag == expr.tag:
            return match_cons(expr.expression, pattern.expression.left, pattern.expression.right, scope)
        case TaggedNode(tag), TaggedNode()\
            if tag == expr.tag\
                and interpret_expression(pattern.expression, scope) == interpret_expression(expr.expression, scope):
            return scope
        case _:
            return None


def match_cons(expr, left, right, scope: Scope) -> Scope | None:
    match left:
        case VariableNode(name, _):
            match expr:
                case ListNode(data=cur, next=rem):
                    left_block = BlockNode(
                        statements=[], expression=cur, parameters=[])
                    new_scope = scope
                    new_scope.current_scope[name] = left_block
                    match right:
                        case ConsNode():
                            return match_cons(rem, right.left, right.right, new_scope)
                        case VariableNode("_", _):
                            return scope
                        case VariableNode(name, _):
                            right_block = BlockNode(
                                statements=[], expression=rem, parameters=[])
                            new_scope.current_scope[name] = right_block
                            return new_scope
                        case ListNode() | NilNode():
                            match match_list(right, rem, new_scope):
                                case None:
                                    return None
                                case new_scope:
                                    return new_scope
                        case _:
                            return None
                case NilNode():
                    return None
        case ListNode() | NilNode():
            match expr:
                case ListNode(data=ListNode(), next=rem) | ListNode(data=NilNode(), next=rem):
                    match match_list(left, expr.data, scope):
                        case None:
                            return None
                        case new_scope:
                            match right:
                                case ConsNode(l, r):
                                    return match_cons(rem, l, r, scope)
                                case VariableNode("_", _):
                                    return scope
                                case VariableNode(name, _):
                                    new_block = BlockNode(
                                        statements=[], expression=rem, parameters=[])
                                    new_scope = scope
                                    new_scope.current_scope[name] = new_block
                                    return new_scope
                                case ListNode() | NilNode():
                                    match match_list(right, rem, scope):
                                        case None:
                                            return None
                                        case new_scope:
                                            return new_scope
                                case _:
                                    return None
        case ConsNode():
            match expr:
                case ListNode(data=ListNode(), next=rem):
                    match match_cons(expr.data, left.left, left.right, scope):
                        case None:
                            return None
                        case new_scope:
                            match right:
                                case ConsNode(l, r):
                                    return match_cons(rem, l, r, scope)
                                case VariableNode("_", _):
                                    return scope
                                case VariableNode(name, _):
                                    new_block = BlockNode(
                                        statements=[], expression=rem, parameters=[])
                                    new_scope = scope
                                    new_scope.current_scope[name] = new_block
                                    return new_scope
                                case ListNode() | NilNode():
                                    match match_list(right, rem, scope):
                                        case None:
                                            return None
                                        case new_scope:
                                            return new_scope
                                case _:
                                    return None
        case _:
            match expr:
                case ListNode(data=cur, next=rem):
                    if interpret_expression(cur, scope) != interpret_expression(left, scope):
                        return None
                    match right:
                        case ConsNode(l, r):
                            return match_cons(rem, l, r, scope)
                        case VariableNode("_", _):
                            return scope
                        case VariableNode(name, _):
                            new_block = BlockNode(
                                statements=[], expression=rem, parameters=[])
                            new_scope = scope
                            new_scope.current_scope[name] = new_block
                            return new_scope
                        case ListNode() | NilNode():
                            match match_list(right, rem, scope):
                                case None:
                                    return None
                                case new_scope:
                                    return new_scope
                        case _:
                            return None
                case NilNode():
                    return None


def interpret_match(expr: ExprNode, case_list: list[ExprNode], scope: Scope) -> ExprNode:

    def head(lst):
        return lst[:1][0]

    def tail(lst):
        return lst[1:]

    if case_list == []:
        InterpreterError("no case to match expression in match expression")
    current_case = head(case_list)
    remaining_cases = tail(case_list)
    match current_case.pattern:
        case ListNode() | NilNode():
            match match_list(current_case.pattern, expr, scope):
                case None:
                    return interpret_match(expr, remaining_cases, scope)
                case new_scope:
                    if not current_case.guard:
                        return interpret_block(current_case.block, new_scope)
                    else:
                        if interpret_expression(current_case.guard, new_scope) == BoolNode(True):
                            return interpret_block(current_case.block, new_scope)
                        else:
                            return interpret_match(expr, remaining_cases, scope)
        case ConsNode(l, r):
            match match_cons(expr, l, r, scope):
                case None:
                    return interpret_match(expr, remaining_cases, scope)
                case new_scope:
                    if not current_case.guard:
                        return interpret_block(current_case.block, new_scope)
                    else:
                        if interpret_expression(current_case.guard, new_scope) == BoolNode(True):
                            return interpret_block(current_case.block, new_scope)
                        else:
                            return interpret_match(expr, remaining_cases, scope)
        case TaggedNode():
            match match_tag(expr, current_case.pattern, scope):
                case None:
                    return interpret_match(expr, remaining_cases, scope)
                case new_scope:
                    if not current_case.guard:
                        return interpret_block(current_case.block, new_scope)
                    else:
                        if interpret_expression(current_case.guard, new_scope) == BoolNode(True):
                            return interpret_block(current_case.block, new_scope)
                        else:
                            return interpret_match(expr, remaining_cases, scope)
        case VariableNode("_", _):
            if not current_case.guard:
                return interpret_block(current_case.block, scope)
            else:
                if interpret_expression(current_case.guard, scope) == BoolNode(True):
                    return interpret_block(current_case.block, scope)
                else:
                    return interpret_match(expr, remaining_cases, scope)

        case VariableNode(namespace, _):
            new_block = BlockNode(
                statements=[], expression=expr, parameters=[])
            scope.current_scope[namespace] = new_block
            if not current_case.guard:
                return interpret_block(current_case.block, scope)
            else:
                if interpret_expression(current_case.guard, scope) == BoolNode(True):
                    return interpret_block(current_case.block, scope)
                else:
                    return interpret_match(expr, remaining_cases, scope)

        case _ as pattern:
            if interpret_predicate(EqNode(pattern, expr), scope) != BoolNode(True):
                return interpret_match(expr, remaining_cases, scope)

            if not current_case.guard:
                return interpret_block(current_case.block, scope)
            else:
                if interpret_expression(current_case.guard, scope) == BoolNode(True):
                    return interpret_block(current_case.block, scope)
                else:
                    return interpret_match(expr, remaining_cases, scope)


def interpret_function(var: VariableNode, scope: Scope) -> ExprNode:

    def split_at_n(l, n) -> tuple[list, list]:
        return l[:n], l[n:]

    def set_params(
            taken: list[str],
            given: list[ExprNode],
            idx: int = 0,
            sd: dict[str, ExprNode | BlockNode] = None) -> dict[str, ExprNode | BlockNode]:
        if sd is None:
            sd = {}

        if idx >= len(taken) and idx >= len(given):
            return sd

        if idx >= len(taken) or idx >= len(given):
            InterpreterError(f"function takes in {len(taken)} parameters, but {
                             len(given)} were taken")

        if isinstance(given[idx], BlockNode):
            sd[taken[idx]] = given[idx]
            return set_params(taken, given, idx+1, sd)

        if not isinstance(given[idx], VariableNode):
            new_block = BlockNode()
            new_block.expression = interpret_expression(given[idx], scope)
            sd[taken[idx]] = new_block
            return set_params(taken, given, idx+1, sd)

        vgiven = get_from_scope(given[idx].namespace, scope)
        if not isinstance(vgiven, BlockNode):
            sd[taken[idx]] = vgiven
            return set_params(taken, given, idx+1, sd)

        if vgiven.parameters and not given[idx].parameters:
            sd[taken[idx]] = vgiven
            return set_params(taken, given, idx+1, sd)

        block = BlockNode()
        block.expression = interpret_expression(given[idx], scope)
        sd[taken[idx]] = block

        return set_params(taken, given, idx+1, sd)
    func = get_from_scope(var.namespace, scope)
    current_params, remaining_params = split_at_n(
        var.parameters, len(func.parameters))

    new_scope = Scope()
    new_scope.outer_scope = scope
    sd = {}
    if func.lexical_scope:
        strings, exprs = func.lexical_scope
        sd = set_params(strings, exprs, sd=sd)

    new_scope.current_scope = set_params(
        func.parameters, current_params, sd=sd
    )
    result = interpret_block(func, new_scope)
    match remaining_params:
        case []:
            return result
        case pl:
            match result:
                case BlockNode(parameters=p, lexical_scope=(s, e)):
                    closure_scope = Scope(set_params(s, e), new_scope)
                    closure_scope.current_scope = set_params(
                        p, pl, sd=closure_scope.current_scope)
                    return interpret_block(result, closure_scope)
                case _:
                    InterpreterError("too many params given")


def get_type(n: ExprNode) -> str:
    match n:
        case _ if isinstance(n, StringNode):
            return "Str"
        case _ if isinstance(n, IntegerNode):
            return "Int"
        case _ if isinstance(n, FloatNode):
            return "Float"
        case _ if isinstance(n, BoolNode):
            return "Bool"
        case _ if isinstance(n, ListNode) or isinstance(n, NilNode):
            return "List"
        case _ if isinstance(n, TaggedNode):
            return n.tag + get_type(n.expression)
        case _:
            InterpreterError(f"Invalid Expression to get type from {n}")


def are_lists_equal(left, right) -> bool:
    match left, right:
        case NilNode(), NilNode():
            return True
        case ListNode(data=ld, next=ln), ListNode(data=rd, next=rn) if ld == rd:
            return are_lists_equal(ln, rn)
        case _:
            return False


def interpret_predicate(node: ExprNode, scope: Scope) -> BoolNode:
    left_node = interpret_expression(node.left, scope)
    right_node = interpret_expression(node.right, scope)
    match node:
        case EqNode():
            if isinstance(left_node, ListNode) or isinstance(left_node, NilNode):
                return BoolNode(are_lists_equal(left_node, right_node))
            elif isinstance(right_node, ListNode) or isinstance(right_node, NilNode):
                return BoolNode(are_lists_equal(left_node, right_node))
            else:
                return BoolNode(left_node.value == right_node.value)
        case NeqNode():
            if isinstance(left_node, ListNode) or isinstance(left_node, NilNode):
                return BoolNode(not are_lists_equal(left_node, right_node))
            elif isinstance(right_node, ListNode) or isinstance(right_node, NilNode):
                return BoolNode(not are_lists_equal(left_node, right_node))
            else:
                return BoolNode(left_node.value != right_node.value)
        case LeqNode():
            return BoolNode(left_node.value <= right_node.value)
        case GeqNode():
            return BoolNode(left_node.value >= right_node.value)
        case LessNode():
            return BoolNode(left_node.value < right_node.value)
        case GreaterNode():
            return BoolNode(left_node.value > right_node.value)
        case other_node:
            InterpreterError(f"not a predicate: {get_type(other_node)}")


def interpret_expression(node: ExprNode, scope: Scope) -> ExprNode:

    def interpret_list(node: ListNode) -> ListNode:
        match node:
            case ListNode():
                return ListNode(
                    interpret_expression(node.data, scope),
                    interpret_list(node.next)
                )
            case NilNode():
                return NilNode()

    def interpret_cons(left: ExprNode, right: ExprNode) -> ListNode:
        left_eval = interpret_expression(left, scope)
        right_eval = interpret_expression(right, scope)
        if (not isinstance(right_eval, ListNode)) and (not isinstance(right_eval, NilNode)):
            InterpreterError("right side of cons should be a list")

        return ListNode(left_eval, right_eval)

    def find_result_type(left: ExprNode, right: ExprNode) -> tuple[str, ExprNode, ExprNode]:

        lt = get_type(left)
        rt = get_type(right)
        match (lt, rt):
            case ("Int", "Int") | ("Float", "Float") | ("Str", "Str"):
                return lt, left, right
            case ("Str", _) | (_, "Str"):
                InterpreterError(f"Type mismatch: {lt} and {rt}")
            case ("Float", _) | (_, "Float"):
                return "Float", FloatNode(left.value), FloatNode(right.value)
            case ("Bool", _) | (_, "Bool"):
                InterpreterError("Cannot apply operations on boolean type")
            case _:
                InterpreterError("unknown result type from operation")

    def apply_binary_operator(
            left: ExprNode,
            right: ExprNode,
            operation: Callable[[ExprNode, ExprNode], ExprNode]) -> ExprNode:

        left_value = interpret_expression(left, scope)
        right_value = interpret_expression(right, scope)
        t, lv, rv = find_result_type(left_value, right_value)
        match t:
            case "Int":
                return IntegerNode(operation(lv.value, rv.value))
            case "Float":
                return FloatNode(operation(lv.value, rv.value))
            case "Str":
                return StringNode(operation(lv.value, rv.value))

    def interpret_negative(node):
        expr = interpret_expression(node.expression, scope)
        match expr:
            case IntegerNode(i):
                return IntegerNode(-i)
            case FloatNode(f):
                return FloatNode(-f)
            case _:
                InterpreterError("only an integer or a float can be negative")

    def interpret_div(left, right):
        left_eval = interpret_expression(left, scope)
        right_eval = interpret_expression(right, scope)
        match left_eval, right_eval:
            case IntegerNode(), IntegerNode():
                return FloatNode(float(left_eval.value) / float(right_eval.value))
            case FloatNode(), FloatNode():
                return FloatNode(left_eval.value / right_eval.value)
            case IntegerNode(), FloatNode() | FloatNode(), IntegerNode():
                return FloatNode(float(left_eval.value) / float(right_eval.value))

    def interpret_cast(to_type, node):
        node_eval = interpret_expression(node, scope)
        if not (isinstance(node_eval, IntegerNode) or isinstance(node_eval, FloatNode) or isinstance(node_eval, StringNode)):
            InterpreterError(f"cannot cast value of {get_type(node_eval)}")
        match to_type:
            case 'int':
                return IntegerNode(int(node_eval.value))
            case 'float':
                return FloatNode(float(node_eval.value))
            case 'string':
                return StringNode(str(node_eval.value))

    if isinstance(node, VariableNode) and node.namespace in ['int', 'float', 'string'] and len(node.parameters) == 1:
        new_scope = Scope(current_scope={}, outer_scope=scope)
        return interpret_cast(node.namespace, node.parameters[0])

    if isinstance(node, VariableNode):
        new_scope = Scope(current_scope={}, outer_scope=scope)
        return interpret_function(node, new_scope)

    if isinstance(node, IfNode):
        return interpret_if(node, scope)

    if isinstance(node, MatchNode):
        eval_expr = interpret_expression(node.expr, scope)
        new_scope = Scope()
        # new_scope.outer_scope = copy.deepcopy(scope)
        new_scope.outer_scope = scope
        new_scope.current_scope = {}
        return interpret_match(eval_expr, node.cases, new_scope)

    match node:
        case NegativeNode():
            return interpret_negative(node)
        case BlockNode():
            return interpret_block(node, scope)
        case ListNode() | NilNode():
            return interpret_list(node)
        case ConsNode():
            return interpret_cons(node.left, node.right)
        case DivNode():
            return interpret_div(node.left, node.right)
        case AddNode():
            return apply_binary_operator(node.left, node.right, lambda x, y: x + y)
        case MultNode():
            return apply_binary_operator(node.left, node.right, lambda x, y: x * y)
        case SubNode():
            return apply_binary_operator(node.left, node.right, lambda x, y: x - y)
        case EqNode() | NeqNode() | GeqNode() | LeqNode() | LessNode() | GreaterNode():
            return interpret_predicate(node, scope)
        case IntegerNode() | StringNode() | FloatNode() | BoolNode() | TaggedNode():
            return node
        case return_node:
            Error(f"Unknown expression type: {get_type(return_node)}")


def interpret_block(node: BlockNode, scope: Scope, statement_idx: int = 0) -> ExprNode:
    if statement_idx >= len(node.statements):
        match node.expression:
            case VariableNode() if node.expression.parameters == []:
                block = get_from_scope(node.expression.namespace, scope)
                match block:
                    case BlockNode(parameters) if parameters != []:
                        # block.lexical_scope = copy.deepcopy(list(
                        #    zip(*[(k, v) for k, v in scope.current_scope.items()])))
                        block.lexical_scope = (list(
                            zip(*[(k, v) for k, v in scope.current_scope.items()])))
                        return block
                    case _:
                        return interpret_block(block, scope)
            case _:
                return interpret_expression(node.expression, scope)

    scope = interpret_statement(node.statements[statement_idx], scope)

    return interpret_block(node, scope, statement_idx + 1)


"""
def interpret_assignment(node: LetNode, scope: Scope) -> Scope:
    new_block = interpret_block(node.expression, scope)
    scope.current_scope[node.namespace] = new_block
    return scope
"""


def interpret_if(node: IfNode, scope: Scope) -> Scope:
    predicate = interpret_expression(node.condition, scope)
    match predicate:
        case BoolNode(True):
            result = interpret_block(node.then_block, scope)
            return result
        case BoolNode(False):
            result = interpret_block(node.else_block, scope)
            return result
        case other_node:
            InterpreterError(f"Condition in if expression must be a boolean, not {
                             get_type(other_node)}.")


def interpret_print(node: PrintNode, scope: Scope) -> None:

    def print_list(list_node: ListNode) -> None:
        match list_node:
            case ListNode(_, next=NilNode()):
                interpret_print(list_node.data, scope)
                print("]", end="")
            case ListNode():
                interpret_print(list_node.data, scope)
                print("; ", end="")
                print_list(list_node.next)
            case NilNode():
                print(']', end='')
                return

    match node:
        case ListNode() | NilNode():
            print('[', end='')
            print_list(node)
        case _:
            evaluated_expression = interpret_expression(node, scope)
            match evaluated_expression:
                case ListNode() | NilNode():
                    print('[', end='')
                    print_list(evaluated_expression)
                case _:
                    print(evaluated_expression.value, end='')


def interpret_statement(node: StatementNode, scope: Scope) -> Scope:
    if isinstance(node, ImportNode):
        with open(node.file_path, 'r') as import_file:
            file_content = import_file.read()
            return interpret(file_content)

    if isinstance(node, LetNode):
        if not node.block.parameters:
            """
            new_scope = Scope(current_scope={},
                              outer_scope=copy.deepcopy(scope))
            """
            new_scope = Scope(current_scope={},
                              outer_scope=(scope))
            result = interpret_block(node.block, new_scope)
            match result:
                case BlockNode():
                    scope.current_scope[node.namespace] = result
                case _:
                    new_block = BlockNode(
                        statements=[], expression=result, parameters=[], lexical_scope=None)
                    scope.current_scope[node.namespace] = new_block
        else:
            scope.current_scope[node.namespace] = node.block

        new_scope = scope
        return new_scope

    if isinstance(node, PrintNode):
        interpret_print(node.expression, scope)
        return scope

    if isinstance(node, PrintLnNode):
        interpret_print(node.expression, scope)
        print()
        return scope

    if isinstance(node, ExprNode):
        v = interpret_expression(node, scope)
        interpret_print(v, scope)
        return scope

    Error("Not yet implemented statement type")


def interpret_program(node: ProgramNode) -> None:

    def interpret_statements(statements: list[StatementNode], idx: int = 0, scope: Scope = Scope()) -> None:

        if idx >= len(statements):
            return scope

        current_scope = interpret_statement(statements[idx], scope)

        return interpret_statements(statements, idx + 1, (current_scope))
        # return interpret_statements(statements, idx + 1, copy.deepcopy(current_scope))

    return interpret_statements(node.statements)


def interpret(input_string: str) -> None:
    tree = parse(input_string)
    if not isinstance(tree, ProgramNode):
        Error("Start node must be of type ProgramNode")

    return interpret_program(tree)
