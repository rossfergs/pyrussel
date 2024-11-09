from typing import Callable

from Token import Token
from TokenType import TokenType
from lexer import lex, peek
from error import Error, ParseError
from ParseNode import (
    ParseNode, ExprNode, AddNode,
    MultNode, SubNode, DivNode,
    IntegerNode, FloatNode, VariableNode,
    StringNode
)


def pp(input_string: str) -> Callable[[ParseNode, int], tuple[ExprNode, int]]:

    def parse_expression(start_idx: int) -> tuple[ExprNode, int]:

        def nud(t: Token, idx: int) -> tuple[ExprNode, int]:
            match t.type:
                case TokenType.STRING:
                    return StringNode(t.literal), idx+1
                case TokenType.FLOAT:
                    return FloatNode(t.literal), idx
                case TokenType.INTEGER:
                    return IntegerNode(t.literal), idx
                case TokenType.NAMESPACE:
                    return VariableNode(t.literal), idx
                case TokenType.OPAR:
                    paren_result, paren_idx = parse(0, idx)
                    next_token, next_idx = lex(input_string, paren_idx)
                    if next_token.type != TokenType.CPAR:
                        ParseError("Unclosed parenthesis")

                    return paren_result, next_idx
                case _:
                    ParseError("Invalid Token in expression")

        def led(left_node: ExprNode, operator: Token, idx: int) -> ExprNode:
            match operator.type:
                case TokenType.ADD:
                    right, current_idx = parse(2, idx)
                    return AddNode(left_node, right), current_idx
                case TokenType.MULT:
                    right, current_idx = parse(3, idx)
                    return MultNode(left_node, right), current_idx
                case TokenType.SUB:
                    right, current_idx = parse(2, idx)
                    return SubNode(left_node, right), current_idx
                case _:
                    print(operator)
                    ParseError("Unknown Operator")

        def get_left_binding_power(t: Token) -> int:
            match t.type:
                case TokenType.ADD | TokenType.SUB:
                    return 2
                case TokenType.MULT:
                    return 3
                case TokenType.EOF:
                    return -1
                case _:
                    return 0

        def collect_expression(left_node: ExprNode, lbp: int,  idx: int) -> tuple[ExprNode, int]:
            current_token, current_idx = lex(input_string, idx)
            if get_left_binding_power(current_token) > lbp:
                expr, current_idx = led(left_node, current_token, current_idx)
                return collect_expression(expr, lbp, current_idx)

            return left_node, idx

        def parse(binding_power: int, idx: int) -> tuple[ExprNode, int]:
            first, first_idx = lex(input_string, idx)
            first_node, first_idx = nud(first, first_idx)
            expression_tree, end_idx = collect_expression(first_node, binding_power, first_idx)

            return expression_tree, end_idx

        return parse(0, start_idx)

    return parse_expression
