from typing import Callable

from Token import Token
from TokenType import TokenType
from lexer import lex
from error import Error, ParseError
from ParseNode import (
    ParseNode, ExprNode, AddNode,
    MultNode, SubNode, DivNode,
    IntegerNode, FloatNode, VariableNode,
    StringNode
)

#  LAMBDRADOR
#    \___/_
#    /\-/\
#    V 0.1


def pp(input_string: str) -> Callable[[ParseNode, int], tuple[ExprNode, int]]:

    def parse_expression(start_idx: int) -> tuple[ExprNode, int]:

        def collect_parameters(idx: int, params: list[ExprNode] = None) -> tuple[list[ExprNode], int]:
            if params is None:
                params = []

            next_token, next_idx = lex(input_string, idx)

            if (next_token.type not in
                    [TokenType.NAMESPACE,
                     TokenType.STRING,
                     TokenType.FLOAT,
                     TokenType.OPAR,
                     TokenType.INTEGER]):
                return params, idx

            if next_token.type == TokenType.NAMESPACE:
                params.append(VariableNode(next_token.literal, []))
                new_params = params
                return collect_parameters(next_idx, new_params)

            next_param, next_idx = nud(next_token, next_idx)
            params.append(next_param)
            new_params = params
            return collect_parameters(next_idx, new_params)

        def nud(t: Token, idx: int) -> tuple[ExprNode, int]:
            match t.type:
                case TokenType.STRING:
                    return StringNode(t.literal), idx + 1
                case TokenType.FLOAT:
                    return FloatNode(float(t.literal)), idx
                case TokenType.INTEGER:
                    return IntegerNode(int(t.literal)), idx
                case TokenType.NAMESPACE:
                    params, next_idx = collect_parameters(idx)
                    return VariableNode(t.literal, params), next_idx
                case TokenType.OPAR:
                    paren_result, paren_idx = parse(0, idx)
                    next_token, next_idx = lex(input_string, paren_idx)
                    if next_token.type != TokenType.CPAR:
                        ParseError("Unclosed parenthesis")

                    # if isinstance(paren_result, VariableNode):
                    #     params, next_idx = collect_parameters(next_idx)
                    #     paren_result.parameters += params

                    return paren_result, next_idx
                case _:
                    ParseError(f"Invalid Token '{t.literal}' in expression")

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
                case TokenType.EOF | TokenType.DELIM:
                    return -1
                case _:
                    return 0

        def collect_expression(left_node: ExprNode, lbp: int, idx: int) -> tuple[ExprNode, int]:
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
