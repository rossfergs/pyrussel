from ParseNode import ParseNode
from lexer import lex
from TokenType import TokenType
from error import ParseError


"""
RSL CF-GRAMMAR RULES

PROGRAM 
    := STATEMENT PROGRAM | EOF

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

    def parse_term(node: ParseNode, idx: int) -> tuple[bool, int]:
        current_token, current_idx = lex(input_string, idx)
        if current_token.type == TokenType.NUMBER:
            return True, current_idx

        if current_token.type == TokenType.STRING:
            # Add another one to index to account for " or '
            return True, current_idx+1

        return False, idx

    def parse_enclosed_expression(node: ParseNode, idx: int) -> tuple[bool, int]:
        current_token, current_idx = lex(input_string, idx)
        if current_token.type != TokenType.OPAR:
            return False, idx

        parse_result, current_idx = parse_expression(node, current_idx)
        if not parse_result:
            return False, idx

        current_token, current_idx = lex(input_string, current_idx)
        if current_token.type != TokenType.CPAR:
            return False, idx

        return True, current_idx

    def parse_binary(node: ParseNode, idx: int) -> tuple[bool, int]:
        current_token, current_idx = lex(input_string, idx)
        if current_token.type not in [TokenType.ADD, TokenType.SUB, TokenType.MULT]:
            return False, idx

        parse_result, current_idx = parse_expression(node, current_idx)
        if not parse_result:
            return False, idx

        return True, current_idx

    def parse_expression(node: ParseNode, idx: int) -> tuple[bool, int]:
        parse_result, current_idx = parse_term(node, idx)
        if parse_result:
            term_idx = current_idx
            parse_result, current_idx = parse_binary(node, current_idx)

            if not parse_result:
                return True, term_idx

            return True, current_idx

        parse_result, current_idx = parse_enclosed_expression(node, idx)
        if parse_result:

            return True, current_idx

        current_token, current_idx = lex(input_string, idx)
        if current_token.type == TokenType.NAMESPACE:
            return True, current_idx

        return False, idx

    def parse_assignment(node: ParseNode, idx: int) -> tuple[bool, int]:
        current_token, current_idx = lex(input_string, idx)
        if current_token.type != TokenType.NAMESPACE:
            return False, idx

        current_token, current_idx = lex(input_string, current_idx)
        if current_token.type != TokenType.EQ:
            return False, idx

        parse_result, current_idx = parse_expression(node, current_idx)
        if not parse_result:
            return False, idx

        return True, current_idx

    def parse_statement(node: ParseNode, idx: int) -> tuple[bool, int]:
        current_token, current_idx = lex(input_string, idx)
        if current_token.type == TokenType.PRINT:
            parse_result, parse_idx = parse_expression(node, current_idx)
            if not parse_result:
                ParseError("invalid expression after PRINT")
            return True, parse_idx

        if current_token.type == TokenType.ASS:
            parse_result, parse_idx = parse_assignment(node, current_idx)
            if not parse_result:
                ParseError("invalid assignment after ASS")
            return True, parse_idx

        parse_result, current_idx = parse_expression(node, idx)
        if parse_result:
            return True, current_idx

        ParseError("invalid statement inner")

    def parse_program(node: ParseNode, idx: int) -> tuple[bool, int]:
        current_token, current_idx = lex(input_string, idx)
        if current_token.type == TokenType.EOF:
            return True, current_idx

        parse_result, current_idx = parse_statement(node, idx)
        if not parse_result:
            ParseError("invalid statement")

        return parse_program(node, current_idx)

    start_node = ParseNode()
    end_result, end_idx = parse_program(start_node, 0)
    if end_result:
        out = "Valid with grammar"
    else:
        out = "Invalid with grammar"
    print(f" => {out}")
