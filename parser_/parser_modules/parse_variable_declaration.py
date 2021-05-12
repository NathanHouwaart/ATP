"""
@file parse_variable_declaration.py
@author Nathan Houwaart (nathan.houwaart@student.hu.nl)
@brief 
@version 0.1
@date 11-05-2021
"""
import sys
import os
import typing

import parser_modules.parse_expression as parse_expr
from misc.token_types import *
from typing import Optional, TypeVar, Callable, List, Tuple
from misc.error_message import generate_error_message
from misc.node_types import *


def parse_variable_declaration(
    characters : str,
    tokens: List['Token']
) -> Tuple['VariableDeclaration', List['Token']]:
    """Function parses a variable declaration
    
    Rules:
        A variable declaration is valid in the following sequence:
        1. TokenTypes.VARIABLE_DECLARATION
        2. TokenTypes.IDENTIFIER
        3. TokenTypes.IS
        4. Any Token that indicates an expression:
            - TokenTypes.CALL
            - TokenTypes.IDENTIFIER
            - TokenTypes.MINUS
            - TokenTypes.PLUS, 
            - TokenTypes.INT
            - TokenTypes.FLOAT
            - TokenTypes.LEFT_PARENTHESIES  
    
    Args:
        characters  : The characters that are being lexed, parsed, interpreted
        tokens      : List of tokens that need to be parsed
    
    Returns:
        If no errors occured:
            Returns a tuple with a variable declaration and a list of tokens that still need to be parsed
        If a grammar error occured:
            Raises a Syntax Error with a message of where the error occured
    """
    variable_declaration, identifier, *tail = tokens
    if identifier.tokentype_ != TokenTypes.IDENTIFIER:
        return generate_error_message(identifier, characters, "Expected identifier after variable declaration", True)
    
    head, *tail = tail
    if head.tokentype_ != TokenTypes.IS:
        return generate_error_message(head, characters, "Expected '='", True)

    head, *tail = tail
    if head.tokentype_ not in (TokenTypes.CALL, TokenTypes.IDENTIFIER, TokenTypes.MINUS, TokenTypes.PLUS, TokenTypes.INT, TokenTypes.FLOAT, TokenTypes.LEFT_PARENTHESIES):
        return generate_error_message(head, characters, "Expected expression after '=' statement", True)
    
    node, tokens = parse_expr.parse_expression(characters, [head] + tail)

    loc_ = {"start": variable_declaration.loc_["start"], "end": node.loc_["end"]}
    range_   = [variable_declaration.range_[0], node.range_[1]]
    node = VariableDeclaration(loc_=loc_, range_=range_,id_=identifier.value_, init_=node)
    return node, tokens