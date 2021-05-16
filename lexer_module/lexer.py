"""
@file lexer.py
@author Nathan Houwaart (nathan.houwaart@student.hu.nl)
@brief This file contains all lexer related functions
@version 0.1
@date 11-05-2021
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re

from typing import Tuple, Callable, Optional
from misc.token_types import *
from misc.error_message import generate_error_message


def search_match(
    characters: str, 
    token_expressions: List[Tuple[str, TokenTypes]], 
    total_index=0
) -> Optional[Tuple[re.match, str]]:
    """Function searches for a matching token expression. Starts searching for a match from the given index.

    Args:
        characters          : The characters that need to be matched.
        token_expressions   : A list of tuples each containing a regex string and identifier.
        total_index         : Try to find a match from this index in characters. Can be seen as characters[total_index:].

    Returns:
        If a match is found:
            A tuple containing a match that has been found and a tag saying what token it has found
        If no match was found:
            A tuple containing (None, None)
    """
    if len(token_expressions) == 0:
        return None, None
    head, *tail = token_expressions
    pattern, tag = head
    
    regex = re.compile(pattern)
    match = regex.match(characters, total_index)
    return (match, tag) if match else search_match(characters, tail, total_index)


def lex(
    characters: str, 
    search_match_f: Callable[[str, List[Tuple[str, TokenTypes]], int], Optional[Tuple[re.match, str]]], 
    token_expressions: List[Tuple[str, TokenTypes]], 
    line_no: int=1, 
    index: int=0, 
    total_index: int=0
) -> List[Token]:
    """Function converts the provided characters into tokens. Uses a provided function to search for matches in characters

    Args:
        characters          : The characters that need to be lexed.
        search_match_f      : A function to match the provided characters with the provided tokens
        token_expressions   : Try to find a match from this index in characters. Can be seen as characters[total_index:].
        line_no             : The current line number that is being lexed, default=1.
        index               : The current line index that is being lexed, default=0.
        total_index         : The total index in characters that is being lexed, default=0

    Returns:
        If no errors occured:
            Returns a list of lexed tokens
        If no match was found:
            Raises a Syntax Error with a message of where the error occured
    """
    if len(characters) == total_index: # If the end characters has been reached return an EOF token
        return [Token(
            loc_={"start":{"line": line_no, "index":index}, "end":{"line": line_no, "index": index+3}}, 
            range_=[total_index,total_index+3] , 
            value_="\00", 
            tokentype_=TokenTypes.EOF
        )]
    
    match, tokentype = search_match_f(characters, token_expressions, total_index)
    if not match:
        generate_error_message(line_no, index, characters, "Invalid Syntax", True)

    matched_text    = match.group(0)
    offset          = match.end(0) - match.start(0)
    token_location  = {"start":{"line": line_no, "index":index}, "end":{"line": line_no, "index": index+offset}}
    token_range     = [match.start(0), match.end(0)]

    token   = Token(loc_=token_location, range_=token_range, value_=matched_text, tokentype_=tokentype)

    if tokentype == TokenTypes.NEW_LINE: line_no +=1; index =0; offset = 0
    return [token] + lex(characters, search_match_f, token_expressions, line_no, index + offset, match.end(0))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No source file provided")
        exit()
    
    with open(sys.argv[1], 'rb') as f:
        code = f.read().decode("utf-8")
    
    lexed = lex(code, search_match, TokenExpressions)
    list(map(print, lexed))