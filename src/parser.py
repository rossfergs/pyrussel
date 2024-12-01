from lexer import lex
from TokenType import TokenType
from error import ParseError
from pratt_parser import pp
from ParseNode import (
    ParseNode, ExprNode, AddNode,
    MultNode, SubNode, DivNode,
    IntegerNode, VariableNode, StringNode,
    PrintNode, LetNode, StatementNode,
    ProgramNode, BlockNode
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


def parse(input_string: str):

    parse_expression = pp(input_string)

    def check_delimiter(idx: int) -> tuple[bool, int]:
        delim_token, delim_idx = lex(input_string, idx)

        if delim_token.type != TokenType.DELIM:
            return False, idx

        return True, delim_idx

    def parse_parameters(idx: int, params: list[str] = None) -> list[str]:
        if params is None:
            params = []

        current_token, current_idx = lex(input_string, idx)
        if current_token.type == TokenType.NAMESPACE:
            params.append(current_token.literal)
            return parse_parameters(current_idx, params)

        if current_token.type != TokenType.EQ:
            ParseError(f"Invalid input parameter: '{current_token.literal}'")

        return params, current_idx

    def parse_assignment(idx: int) -> tuple[StatementNode, int]:
        current_token, current_idx = lex(input_string, idx)
        if current_token.type != TokenType.NAMESPACE:
            return False, idx

        namespace = current_token.literal

        input_parameters, current_idx = parse_parameters(current_idx)

        block_node, current_idx = parse_block(current_idx, input_parameters)
        if block_node is None:
            return False, idx

        delim_present, end_idx = check_delimiter(current_idx)
        if not delim_present:
            ParseError("Delimiter required after let")

        return LetNode(namespace, block_node), end_idx

    def parse_print(idx: int) -> tuple[StatementNode, int]:
        expr_node, current_idx = parse_expression(idx)

        if expr_node is None:
            ParseError("Invalid expression after print")

        delim_present, end_idx = check_delimiter(current_idx)
        if not delim_present:
            ParseError("Delimiter required after print")

        return PrintNode(expr_node), end_idx

    def parse_statement(idx: int) -> tuple[StatementNode, int]:
        current_token, current_idx = lex(input_string, idx)
        if current_token.type == TokenType.PRINT:
            return parse_print(current_idx)

        if current_token.type == TokenType.ASS:
            expr_node, parse_idx = parse_assignment(current_idx)
            if expr_node is None:
                ParseError("invalid assignment after ASS")

            return expr_node, parse_idx

        # ParseError(f"Unrecognised Statement '{current_token.literal}'")

        parse_result, current_idx = parse_expression(idx)
        if parse_result is not None:
            return parse_result, current_idx

        ParseError("invalid statement inner")

    def parse_block(idx: int,
                    input_params: list[str],
                    statement_list: list[StatementNode] = None) -> tuple[BlockNode, int]:

        if statement_list is None:
            statement_list = []

        statement, current_idx = parse_statement(idx)
        if isinstance(statement, ExprNode):
            return BlockNode(input_params, statement_list, statement), current_idx

        statement_list.append(statement)
        return parse_block(current_idx, input_params, statement_list)

    def parse_program(idx: int, statement_list=None) -> ProgramNode:
        if statement_list is None:
            statement_list = []

        current_token, current_idx = lex(input_string, idx)
        if current_token.type == TokenType.EOF:
            return ProgramNode(statement_list)

        statement_node, current_idx = parse_statement(idx)
        if statement_node is None:
            ParseError("invalid statement")

        statement_list.append(statement_node)

        return parse_program(current_idx, statement_list)

    def print_node(node, indent=0):
        spacing = "    " * indent
        if isinstance(node, ProgramNode):
            for statement in node.statements:
                print_node(statement, indent + 1)
        elif isinstance(node, LetNode):
            print(f"{spacing}{node}")
            print_node(node.namespace, indent + 1)
            print_node(node.block, indent + 1)
        elif isinstance(node, PrintNode):
            print(f"{spacing}{node}")
            print_node(node.expression, indent + 1)
        elif isinstance(node, VariableNode):
            print(f"{spacing}{node}")
        elif isinstance(node, IntegerNode):
            print(f"{spacing}{node}")
        elif isinstance(node, AddNode) or isinstance(node, SubNode) or isinstance(node, MultNode):
            print(f"{spacing}{node}")
            print_node(node.left, indent + 1)
            print_node(node.right, indent + 1)

    end_result = parse_program(0)
    # print_node(end_result)
    return end_result
