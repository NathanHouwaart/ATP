"""
@file parser.py
@author Nathan Houwaart (nathan.houwaart@student.hu.nl)
@brief This file main parser functions
@version 0.1
@date 11-05-2021
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print(sys.path)

from lexer.lexer import lex, search_match
from misc.token_types import *
from misc.node_types import *
from typing import Optional, TypeVar, Callable, List, Tuple
from misc.error_message import generate_error_message

import parser_modules.parse_variable_declaration 
import parser_modules.parse_function_declaration
import parser_modules.parse_if_statement
import parser_modules.parse_function_call

def parse(
    characters: str, 
    tokens: List['Token'], 
    termination_tokens: List['TokenTypes']=[], 
) -> List['Node']:
    """Function creates an AST from the provided tokens. It raises error 
    messages when it encounters illegal grammar
    
    Args:
        characters          : Characters that are being lexed, parsed and interpreted
        tokens              : List of tokens to create an AST from
        termination_tokens  : A List of termination tokens. If the parser encounters one of these tokens OR an EOF token, stop parsing

    Returns:
        If no errors occured:
            - An AST in the form of a program node
            - An EOF Token
        If a grammar error occured:
            Raises a Syntax Error with a message of where the error occured
    """
    if len(tokens) == 0: return [], []
    
    head, *tail = tokens
    if   head.tokentype_ in (TokenTypes.EOF, *termination_tokens) : return [], tail
    elif head.tokentype_ in (TokenTypes.NEW_LINE, TokenTypes.TAB) : return parse(characters, tail, termination_tokens)
    elif head.tokentype_ == TokenTypes.VARIABLE_DECLARATION       : node, tokens = parser_modules.parse_variable_declaration.parse_variable_declaration(characters, tail)
    elif head.tokentype_ == TokenTypes.FUNCTION_DECLARATION       : node, tokens = parser_modules.parse_function_declaration.parse_function_declaration(characters, tail)
    elif head.tokentype_ == TokenTypes.IF                         : node, tokens = parser_modules.parse_if_statement.parse_if_statement(characters, tail)
    elif head.tokentype_ == TokenTypes.RETURN                     : node, tokens = parser_modules.parse_function_declaration.parse_return_statement(characters, tail)
    elif head.tokentype_ == TokenTypes.CALL                       : node, tokens = parser_modules.parse_function_call.parse_function_call(characters, tail)
    else                                                          : return generate_error_message(head, characters, "Invalid Syntax", True)
    nodes, tokens = parse(characters, tokens, termination_tokens)
    return [node] + nodes, tokens

if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #     print("No source file provided")
    #     exit()
    
    with open("simple_language.py", 'rb') as f:
        code = f.read().decode("utf-8")
    
    lexed = lex(code, search_match, TokenExpressions)
    tokens = list(filter(lambda token: token.tokentype_ != TokenTypes.NONE, lexed))
    list(map(print, lexed)) 

    parsed, eof_token = parse(code, tokens)
    program = Program(loc_={'start': {'line': 1, 'index': 0}, "end":{"line":tokens[-1].loc_["start"]["line"], "index":tokens[-1].loc_["start"]["index"]}}, range_=[0, len(code)], body_=parsed)
    
    
    # print(str(program))
    with open("pretty_printed.json", "w") as f:
        f.write(program.pretty_print())