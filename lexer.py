from typing import *
import operator
from token_s import Token
from token_types import *
import sys
import re

A = TypeVar('A')
def match_token(characters: str, token_expressions: List[A]):
    if len(token_expressions) == 0:
        return []
    head, *tail = token_expressions
    pattern, tag = head
    
    regex = re.compile(pattern)
    match = regex.match(characters)

    if match:
        text = match.group(0)
        if tag:
            token = (text, tag)
            return ([token], match.end(0))
    return match_token(characters, tail)


A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')
D = TypeVar('D')
def lex(characters: str, match_token_f: Callable[[A,B], Tuple[C, D]], token_expressions: List[B]) -> List[C]:
    if len(characters) == 0:
        return []
    token, offset = match_token_f(characters, token_expressions)
    head, *tail = characters
    return token + lex(characters[offset:], match_token_f, token_expressions)


if __name__=="__main__":
    if len(sys.argv) <= 1:
        print("No source file provided!")
        exit()

    with open(sys.argv[1], 'r') as f:
        code = f.read()

    tokens = lex(code, match_token, TokenExpressions)
    
    for token in tokens:
        print(token)