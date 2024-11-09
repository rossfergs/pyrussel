from typing import Callable

from Token import Token
from TokenType import TokenType
from error import LexerError


def skip_whitespace(input_string: str, idx: int) -> int:
    if idx >= len(input_string):
        return idx

    if input_string[idx] == " ":
        return skip_whitespace(input_string, idx+1)

    return idx


def collect(
        input_string: str,
        idx: int,
        token_type: TokenType,
        char_check: Callable[[str], bool],
        end_char: Callable[[int], bool],
        literal="") -> tuple[Token, int]:

    if idx >= len(input_string) or end_char(input_string[idx]):
        return Token(token_type, literal), idx

    if char_check(input_string[idx]):
        return collect(input_string, idx+1, token_type, char_check, end_char, literal+input_string[idx])

    match token_type:
        case TokenType.NUMBER:
            LexerError("non-numeric character in number.")
        case TokenType.STRING:
            LexerError("non-numeric character in string.")
        case TokenType.NAMESPACE:
            LexerError("invalid character in namespace symbol.")
        case _:
            LexerError("unexpected character in multi-character token.")


def collect_namespace_token(input_string: str, idx: int) -> tuple[Token, int]:
    return collect(
        input_string,
        idx,
        TokenType.NAMESPACE,
        lambda x: x.isalnum() or x == '_',
        lambda x: x in [" ", ")", ";", "]", ".", "+", "-", "*"])


def collect_string_literal(input_string: str, idx: int, end_quote: str) -> tuple[Token, int]:
    return collect(
        input_string,
        idx,
        TokenType.STRING,
        lambda x: True,
        lambda x: x == end_quote)


def collect_number_token(input_string: str, idx: int) -> tuple[Token, int]:
    number, current_idx = collect(
        input_string,
        idx,
        TokenType.NUMBER,
        lambda x: '0' <= x <= '9' or x == '.',
        lambda x: x in [" ", ")", ";", "+", "=", "*", "-"])

    if '.' in number.literal:
        return Token(TokenType.FLOAT, number.literal), current_idx

    return Token(TokenType.INTEGER, number.literal), current_idx


def collect_and_classify_token(input_string: str, idx: int) -> tuple[Token, int]:
    token_info, token_idx = collect_namespace_token(input_string, idx)
    match token_info.literal:
        case "let":
            return Token(TokenType.ASS, token_info.literal), token_idx
        case "print":
            return Token(TokenType.PRINT, token_info.literal), token_idx
        case _:
            return token_info, token_idx


def lex(input_string: str, idx: int) -> tuple[Token, int]:
    idx = skip_whitespace(input_string, idx)
    if idx >= len(input_string):
        return Token(TokenType.EOF, "EOF"), idx
    ch = input_string[idx]
    match ch:
        case ch if '0' <= ch <= '9':
            return collect_number_token(input_string, idx)
        case "'" | "\"":
            return collect_string_literal(input_string, idx+1, ch)
        case ch if ch.isalnum():
            return collect_and_classify_token(input_string, idx)
        case '(':
            return Token(TokenType.OPAR, ch), idx+1
        case ')':
            return Token(TokenType.CPAR, ch), idx+1
        case '*':
            return Token(TokenType.MULT, ch), idx+1
        case '+':
            return Token(TokenType.ADD, ch), idx+1
        case '-':
            return Token(TokenType.SUB, ch), idx+1
        case ';':
            return Token(TokenType.DLM, ch), idx+1
        case '\n':
            return Token(TokenType.EOF, ch), idx+1
        case '=':
            return Token(TokenType.EQ, ch), idx+1
        case _:
            LexerError(f"Unrecognised character: {ch}")


def peek(input_string: str, idx: int) -> tuple[Token, int]:
    first_token, first_idx = lex(input_string, idx)
    peeked_token, peeked_idx = lex(input_string, first_idx)
    return peeked_token, peeked_idx
