from typing import *
import operator
from token import Token
from token_types import *
from parser_node_types import *
import sys
import re


class Tree(NamedTuple):
    left : Union['Tree', int]
    right : Union['Tree', int]

A = TypeVar('A')
def search_match(characters: str, token_expressions: List[A], line_no=1, total_index=0) -> Optional[A]:
    if len(token_expressions) == 0:
        return None, None
    head, *tail = token_expressions
    pattern, tag = head
    
    regex = re.compile(pattern)
    match = regex.match(characters, total_index)
    return (match, tag) if match else search_match(characters, tail, line_no, total_index)


A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')
D = TypeVar('D')
def lex(characters: str, search_match_f: Callable[[A,B], Tuple[C, D]], token_expressions: List[B], line_no: int=1, index: int=0, total_index: int=0) -> Tuple[List[C], Optional[str]]:
    if len(characters) == total_index:
        token_loc={"start":{"line": line_no, "index":index}}
        token_range=[total_index,total_index+2]  
        return [Token(loc_=token_loc, range_=token_range, value_="\00", tokentype_=TokenTypes.EOF)]
    
    match, tokentype = search_match_f(characters, token_expressions, line_no, total_index)
    if not match: raise Exception(f"invalid syntax: {characters[total_index:].split()[0]}")

    text    = match.group(0)
    offset  = match.end(0) - match.start(0)

    token_loc={"start":{"line": line_no, "index":index}}
    token_range = [match.start(0), match.end(0)]

    token   = Token(loc_=token_loc, range_=token_range, value_=text, tokentype_=tokentype)

    if tokentype == TokenTypes.NEW_LINE: line_no +=1; index =0; offset = 0
    return [token] + lex(characters, search_match_f, token_expressions, line_no, index + offset, match.end(0))

def parse_number(tokens) -> Optional[None]:
    """factor : INTEGER | LPAREN expr RPAREN"""
    head, *tail = tokens
    if head.token_type in (TokenTypes.PLUS, TokenTypes.MINUS):
        node, tail = parse_number(tail)
        return UnaryOperator(head, node), tail
    elif head.token_type == TokenTypes.NONE:
        return parse_number(tail)
    else:
        return parse_power(tokens)

def parse_power(tokens):
    head, *tail, tokens
    node, tokens = parse_number(tokens)
    return BinaryOperator(node, head, )

def parse_term(tokens):
    node, tokens = parse_number(tokens)
    node, tokens = loop(node, tokens, (TokenTypes.MULTIPLY, TokenTypes.DIVIDE))
    return node, tokens

def parse_atom(tokens):
    head, *tail = tokens
    if head.token_type in (TokenTypes.INT, TokenTypes.FLOAT):
        return NumberNode(head), tail
    elif head.token_type == TokenTypes.LEFT_PARENTHESIES:
        node, tokens = parse_expr(tail)
        head, *tail = tokens
        return node, tail
    elif head.token_type == TokenTypes.NONE:
        return parse_atom(tail)

def loop(node, tokens, token_types):
    head, *tail = tokens
    if head.token_type in token_types:
        token = head
        right, tokens = parse_term(tail)
        node = BinaryOperator(left=node, operator=token, right=right)
        return loop(node, tokens, token_types)
    if head.token_type == TokenTypes.NONE:
        return loop(node, tail, token_types)
    return node, tokens

def parse_expr(tokens):
    head, *tail = tokens
    if head.token_type == TokenTypes.VARIABLE_DECLARATION:
        head, *tail = tail
        head, *tail = tail
        if head.token_type != TokenTypes.IDENTIFIER:
            print("Syntax error, Expected identifier")
            exit()
        variable_name = head
        head, *tail = tail
        if head.token_type != TokenTypes.IS:
            print("Syntax error, Expected '='")
            exit()
        
        return parse_expr(tail)
        
    
    node, tokens = parse_term(tokens)
    node, tokens = loop(node, tokens, (TokenTypes.MINUS, TokenTypes.PLUS))

    return node, tokens
    
A = TypeVar('A')
def parse(tokens: list[A], index: int = 0):
    if len(tokens) == 0:
        return []
    return parse_expr(tokens)
        
    
    
    

if __name__=="__main__":
    # if len(sys.argv) <= 1:
    #     print("No source file provided!")
    #     exit()

    with open("simple_language.py", 'rb') as f: #"new_language.py"
        code = f.read().decode("utf-8")

    tokens = lex(code, search_match, TokenExpressions)
    print("Tokens:")
    list(map(print, tokens))
    print("\n")
    parsed, leftover_tokens = parse(tokens)
    print("Parsed")
    print(parsed)
    print(type(parsed))
    print(leftover_tokens)