from lexer import lex
from typing import Callable
from TokenType import TokenType
from error import ParseError
from Token import Token
from ParseNode import (
    ParseNode, ExprNode, AddNode,
    MultNode, SubNode, DivNode,
    IntegerNode, VariableNode, StringNode,
    PrintNode, LetNode, StatementNode,
    ProgramNode, BlockNode, IfNode,
    PrintLnNode, ListNode, NilNode,
    ConsNode, BoolNode, GeqNode,
    GreaterNode, LeqNode, LessNode,
    EqNode, NeqNode, FloatNode,
    MatchNode, CaseNode
)


"""
RSL CF-GRAMMAR RULES

PROGRAM
    := STATEMENT PROGRAM | EOF

BLOCK
    := STATEMENT BLOCK | EXPRESSION

STATEMENT
    := print EXPRESSION;
    := let namespace PARAMETERS = BLOCK;
    := EXPRESSION

PARAMETERS
    := namespace PARAMETERS | None

EXPRESSION
    := namespace ARGUMENTS
    := TERM OPERATOR EXPRESSION
    := TERM
    := ( EXPRESSION )

ARGUMENTS
    := EXPRESSION ARGUMENTS | None

TERM
    := STRING
    := NUMBER

NUMBER
    := DIGIT NUMBER
    := DIGIT

DIGIT
    := 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9

STRING
    := CHARACTER STRING
    := CHARACTER

CHARACTER
    := [Any Character]
"""


def parse_expression_wrapper(input_string: str, idx: int) -> tuple[ExprNode, int]:
    parse_expression = pp(input_string)
    return parse_expression(idx)


def parse_match(input_string: str, idx: int):

    expr, expr_idx = parse_expression_wrapper(input_string, idx)

    with_tok, with_idx = lex(input_string, expr_idx)
    if with_tok.type != TokenType.WITH:
        ParseError("with needed after expression in match")

    cases, cases_idx = parse_case(input_string, with_idx)
    return MatchNode(expr, cases), cases_idx


def parse_case(input_string: str, idx: int, case_list=None) -> tuple[list[ExprNode], int]:
    if not case_list:
        case_list = []

    case_tok, case_idx = lex(input_string, idx)
    if case_tok.type != TokenType.CASE:
        return case_list, idx

    pattern, pattern_idx = parse_expression_wrapper(input_string, case_idx)

    when_tok, when_idx = lex(input_string, pattern_idx)
    if when_tok.type == TokenType.WHEN:
        guard, guard_idx = parse_expression_wrapper(input_string, when_idx)
        then_tok, then_idx = lex(input_string, guard_idx)
        if then_tok.type != TokenType.THEN:
            ParseError("then required in case")
        block, block_idx = parse_block(input_string, then_idx, [])
        case_list.append(CaseNode(pattern, guard, block))
        return parse_case(input_string, block_idx, case_list=case_list)
    else:
        then_tok, then_idx = lex(input_string, pattern_idx)
        if then_tok.type != TokenType.THEN:
            ParseError("then required in case")
        block, block_idx = parse_block(input_string, then_idx, [])
        case_list.append(CaseNode(pattern, None, block))
        return parse_case(input_string, block_idx, case_list=case_list)


def parse_if(input_string: str, idx: int) -> tuple[ExprNode, int]:
    condition, next_idx = parse_expression_wrapper(input_string, idx)

    then_tok, then_idx = lex(input_string, next_idx)
    if then_tok.type != TokenType.THEN:
        ParseError("'then' required in if expression")

    then_block, then_block_idx = parse_block(input_string, then_idx, [])

    else_tok, else_idx = lex(input_string, then_block_idx)
    if else_tok.type != TokenType.ELSE:
        ParseError("'else' required in else expression")

    else_block, else_block_idx = parse_block(input_string, else_idx, [])

    return IfNode(condition, then_block, else_block), else_block_idx


def parse_parameters(input_string: str, idx: int, params: list[str] = None) -> list[str]:
    if params is None:
        params = []

    current_token, current_idx = lex(input_string, idx)
    if current_token.type == TokenType.NAMESPACE:
        params.append(current_token.literal)
        return parse_parameters(input_string, current_idx, params)

    if current_token.type != TokenType.EQ:
        ParseError(f"Invalid input parameter: '{current_token.literal}'")

    return params, current_idx


def parse_assignment(input_string: str, idx: int) -> tuple[StatementNode, int]:
    current_token, current_idx = lex(input_string, idx)
    if current_token.type != TokenType.NAMESPACE:
        return False, idx

    namespace = current_token.literal

    input_parameters, current_idx = parse_parameters(input_string, current_idx)

    block_node, current_idx = parse_block(
        input_string, current_idx, input_parameters)
    if block_node is None:
        return False, idx

    return LetNode(namespace, block_node), current_idx


def parse_print(input_string: str, idx: int) -> tuple[StatementNode, int]:
    expr_node, current_idx = parse_expression_wrapper(input_string, idx)

    if expr_node is None:
        ParseError("Invalid expression after print")

    return PrintNode(expr_node), current_idx


def parse_println(input_string: str, idx: int) -> tuple[StatementNode, int]:
    expr_node, current_idx = parse_expression_wrapper(input_string, idx)

    if expr_node is None:
        ParseError("Invalid expression after print")

    return PrintLnNode(expr_node), current_idx


def parse_statement(input_string: str, idx: int) -> tuple[StatementNode, int]:
    current_token, current_idx = lex(input_string, idx)
    if current_token.type == TokenType.PRINT:
        return parse_print(input_string, current_idx)

    if current_token.type == TokenType.PRINTLN:
        return parse_println(input_string, current_idx)

    if current_token.type == TokenType.ASS:
        expr_node, parse_idx = parse_assignment(input_string, current_idx)
        if expr_node is None:
            ParseError("invalid assignment after ASS")

        return expr_node, parse_idx

    parse_result, current_idx = parse_expression_wrapper(input_string, idx)
    if parse_result is not None:
        return parse_result, current_idx

    ParseError("invalid statement or expression")


def parse_block(input_string: str, idx: int,
                input_params: list[str],
                statement_list: list[StatementNode] = None) -> tuple[BlockNode, int]:

    if statement_list is None:
        statement_list = []

    statement, current_idx = parse_statement(input_string, idx)
    if isinstance(statement, ExprNode):
        return BlockNode(input_params, statement_list, statement), current_idx
    next_node, next_idx = lex(input_string, current_idx)
    if next_node.type != TokenType.DELIM:
        ParseError("delim required after statement in block")
    statement_list.append(statement)
    return parse_block(input_string, next_idx, input_params, statement_list)


def parse_program(input_string: str, idx: int, statement_list=None) -> ProgramNode:
    if statement_list is None:
        statement_list = []

    current_token, current_idx = lex(input_string, idx)
    if current_token.type == TokenType.EOF:
        return ProgramNode(statement_list)

    statement_node, current_idx = parse_statement(input_string, idx)
    if statement_node is None:
        ParseError("invalid statement")

    statement_list.append(statement_node)

    return parse_program(input_string, current_idx, statement_list)


def parse(input_string):
    end_result = parse_program(input_string, 0)
    return end_result


def pp(input_string: str) -> Callable[[ParseNode, int], tuple[ExprNode, int]]:

    def parse_expression(start_idx: int) -> tuple[ExprNode, int]:

        def parse_list(idx: int) -> tuple[ExprNode, int]:
            tok, tok_idx = lex(input_string, idx)
            if tok.type == TokenType.CSQP:
                return (NilNode(), tok_idx)
            expr, expr_idx = nud(tok, tok_idx)
            next_token, next_idx = lex(input_string, expr_idx)
            match next_token.type:
                case TokenType.CSQP:
                    return (ListNode(expr, NilNode()), next_idx)
                case TokenType.DELIM:
                    remainder, end_idx = parse_list(next_idx)
                    return (ListNode(expr, remainder), end_idx)
                case _:
                    ParseError("unmatched in parsing list")

        def collect_parameters(idx: int, params: list[ExprNode] = None) -> tuple[list[ExprNode], int]:
            if params is None:
                params = []

            next_token, next_idx = lex(input_string, idx)

            if (next_token.type not in
               [TokenType.NAMESPACE,
                TokenType.STRING,
                TokenType.FLOAT,
                TokenType.OPAR,
                TokenType.INTEGER,
                    TokenType.OSQP]):
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
                case TokenType.MATCH:
                    return parse_match(input_string, idx)
                case TokenType.IF:
                    return parse_if(input_string, idx)
                case TokenType.OSQP:
                    return parse_list(idx)
                case TokenType.STRING:
                    return StringNode(t.literal), idx + 1
                case TokenType.FLOAT:
                    return FloatNode(float(t.literal)), idx
                case TokenType.INTEGER:
                    return IntegerNode(int(t.literal)), idx
                case TokenType.BOOL:
                    if t.literal == "false":
                        return BoolNode(False), idx
                    else:
                        return BoolNode(True), idx
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
                    ParseError(f"Invalid Token '{
                               t.literal}' in expression")

        def led(left_node: ExprNode, operator: Token, idx: int) -> ExprNode:
            lbp = get_left_binding_power(operator)
            if operator.type == TokenType.CONS:
                lbp -= 1
            right_node, current_idx = parse(lbp, idx)
            match operator.type:
                case TokenType.CONS:
                    return ConsNode(left_node, right_node), current_idx
                case TokenType.ADD:
                    return AddNode(left_node, right_node), current_idx
                case TokenType.MULT:
                    return MultNode(left_node, right_node), current_idx
                case TokenType.SUB:
                    return SubNode(left_node, right_node), current_idx
                case TokenType.EQ:
                    return EqNode(left_node, right_node), current_idx
                case TokenType.NEQ:
                    return NeqNode(left_node, right_node), current_idx
                case TokenType.GEQ:
                    return GeqNode(left_node, right_node), current_idx
                case TokenType.LEQ:
                    return LeqNode(left_node, right_node), current_idx
                case TokenType.LESS:
                    return LessNode(left_node, right_node), current_idx
                case TokenType.GREATER:
                    return GreaterNode(left_node, right_node), current_idx
                case _:
                    ParseError(f"Unknown Operator {left_node}")

        def get_left_binding_power(t: Token) -> int:
            match t.type:
                case TokenType.EQ | TokenType.NEQ | TokenType.GEQ | TokenType.LEQ | TokenType.LESS | TokenType.GREATER:
                    return 5
                case TokenType.ADD | TokenType.SUB | TokenType.CONS:
                    return 2
                case TokenType.MULT:
                    return 3
                case _:
                    return -1

        def collect_expression(left_node: ExprNode, lbp: int, idx: int) -> tuple[ExprNode, int]:
            current_token, current_idx = lex(input_string, idx)
            if get_left_binding_power(current_token) >= lbp:
                expr, current_idx = led(
                    left_node, current_token, current_idx)
                return collect_expression(expr, lbp, current_idx)

            return left_node, idx

        def parse(binding_power: int, idx: int) -> tuple[ExprNode, int]:
            first, first_idx = lex(input_string, idx)
            first_node, first_node_idx = nud(first, first_idx)
            expression_tree, end_idx = collect_expression(
                first_node, binding_power, first_node_idx)

            return expression_tree, end_idx

        return parse(0, start_idx)

    return parse_expression
