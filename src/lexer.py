from typing import Callable

from token import Token
from TokenType import TokenType
from error import LexerError


def end_of_expression(ch: str) -> bool:
    match ch:
        case ' ' | '\n' | '\t' | '\r':
            return True
        case _:
            return False


def skip_whitespace(input_string: str, idx: int) -> int:
    while input_string[idx] == " ":
        idx += 1
    return idx


def collect(
        input_string: str,
        idx: int,
        token_type: TokenType,
        char_check: Callable[[str], bool],
        end_char: Callable[[int], bool],
        literal="") -> tuple[Token, int]:

    if end_char(input_string[idx]) or idx == len(input_string):
        return Token(token_type, literal), idx - 1

    if char_check(input_string[idx]):
        return collect(input_string, idx + 1, literal+input_string[idx])

    match token_type:
        case TokenType.NUMBER:
            LexerError("non-numeric character in number.")
        case TokenType.STRING:
            LexerError("non-numeric character in string.")
        case TokenType.NAMESPACE:
            LexerError("non-numeric character in namespace symbol.")
        case _:
            LexerError("unexpected character in multi-character token.")


def collect_namespace_token(input_string: str, idx: int) -> tuple[Token, int]:
    return collect(
        input_string,
        0,
        TokenType.NAMESPACE,
        lambda x: x.isalnum(),
        lambda x: x in [" ", ")", ";", "]"])


def collect_string_literal(input_string: str, idx: int, end_quote: str) -> tuple[Token, int]:
    return collect(
        input_string,
        idx,
        TokenType.STRING,
        lambda x: True,
        lambda x: x == end_quote)


def collect_number_token(input_string: str, idx: int) -> tuple[Token, int]:
    return collect(
        input_string,
        idx,
        TokenType.NUMBER,
        lambda x: '0' <= x <= '9' or x == '.',
        lambda x: x in [" ", ")", ";"])


def lex(input_string: str, idx: int) -> tuple[Token, int]:
    if input_string[idx] == " ":
        idx = skip_whitespace(input_string, idx)
    ch = input_string[idx]
    match ch:
        case ch if '0' <= ch <= '9':
            return collect_number_token(input_string, idx)
        case "'" | "\"":
            return collect_string_literal(input_string, idx, ch)
        case ch if ch.isalnum():
            return collect_namespace_token(input_string, idx)
        case '(':
            return Token(ch, TokenType.OPENPAREN), idx
        case ')':
            return Token(ch, TokenType.CLOSEPAREN), idx
        case '*':
            return Token(ch, TokenType.MULT), idx
        case '+':
            return Token(ch, TokenType.ADD), idx
        case '-':
            return Token(ch, TokenType.MINUS), idx
        case ';':
            return Token(ch, TokenType.DLM), idx
        case _:
            LexerError(f"Unrecognised character: {ch}")
