from lexer import lex, peek
from TokenType import TokenType
from error import ParseError
from pratt_parser import pp
from ParseNode import (
    ParseNode, ExprNode, AddNode,
    MultNode, SubNode, DivNode,
    IntegerNode, VariableNode, StringNode,
    PrintNode, LetNode, StatementNode,
    ProgramNode
)


"""
RSL CF-GRAMMAR RULES

PROGRAM 
    := STATEMENT PROGRAM | EOF
    
BLOCK
    := STATEMENT BLOCK | EXPRESSION

STATEMENT 
    := print EXPRESSION
    := let namespace = EXPRESSION
    := EXPRESSION

EXPRESSION
    := TERM OPERATOR EXPRESSION
    := TERM
    := ( EXPRESSION )
    
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

    def parse_assignment(idx: int) -> tuple[StatementNode, int]:

        current_token, current_idx = lex(input_string, idx)
        if current_token.type != TokenType.NAMESPACE:
            return False, idx

        namespace_node = current_token.literal

        current_token, current_idx = lex(input_string, current_idx)
        if current_token.type != TokenType.EQ:
            return False, idx

        expr_node, current_idx = parse_expression(current_idx)
        if expr_node is None:
            return False, idx

        return LetNode(namespace_node, expr_node), current_idx

    def parse_print(idx: int) -> tuple[StatementNode, int]:
        expr_node, current_idx = parse_expression(idx)

        if expr_node is None:
            ParseError("Invalid expression after PRINT")

        return PrintNode(expr_node), current_idx

    def parse_statement(idx: int) -> tuple[StatementNode, int]:
        current_token, current_idx = lex(input_string, idx)
        if current_token.type == TokenType.PRINT:
            return parse_print(current_idx)

        if current_token.type == TokenType.ASS:
            expr_node, parse_idx = parse_assignment(current_idx)
            if expr_node is None:
                ParseError("invalid assignment after ASS")
            return expr_node, parse_idx

        parse_result, current_idx = parse_expression(idx)
        if parse_result is not None:
            return parse_result, current_idx

        ParseError("invalid statement inner")

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
            print_node(node.expression, indent + 1)
        elif isinstance(node, PrintNode):
            print(f"{spacing}{node}")
            print_node(node.expression, indent + 1)
        elif isinstance(node, VariableNode):
            print(f"{spacing}{node}")
        elif isinstance(node, IntegerNode):
            print(f"{spacing}{node}")
        elif isinstance(node, AddNode) or isinstance(node, SubNode) or isinstance(node, MultNode):
            print(f"{spacing}{node}")
            print_node(node.leftNode, indent + 1)
            print_node(node.rightNode, indent + 1)
    end_result = parse_program(0)
    return end_result
