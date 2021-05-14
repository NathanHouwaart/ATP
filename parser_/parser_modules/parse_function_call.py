"""
@file parse_function_call.py
@author Nathan Houwaart (nathan.houwaart@student.hu.nl)
@brief This file contains functions to parse a function call
@version 0.1
@date 11-05-2021
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from misc.node_types import *
from misc.token_types import TokenTypes, Token
from typing import Optional, List, Tuple
from misc.error_message import generate_error_message

import parser_modules.parse_expression as parse_expr

def parse_function_call_parameters_loop(
    characters: str,
    tokens : List[Token]
) -> Tuple[List['Node'], List['Token']]:
    node, tokens = parse_expr.parse_expression(characters, tokens)
    head, *tail = tokens
    if head.tokentype_ == TokenTypes.CALL: 
        return [node], tokens
    if head.tokentype_ != TokenTypes.SEPARATOR:
        generate_error_message(head, characters, "Missing '|' between multiple parameters", True)

    nodes, tokens = parse_function_call_parameters_loop(characters, tail)
    return [node] + nodes, tokens

def parse_function_call_parameters(
    characters: str, 
    tokens : List['Token']
) -> Tuple[List['Node'], List['Token']]:
    """Function tries to parse a function call parameters
    
    Note: 
        Follows the following grammar rules:
            1. A function call statement starts with a TokenType.CALL and 
                ends with a TokenType.CALL
            2. A function call parameter must be separated by a '|'
    
    Args:
        characters  : The characters that are being lexed, parsed, interpreted
        tokens      : List of tokens that need to be parsed
    
    Returns:
        If no errors occured:
            - A list of nodes representing the parameters 
            - A list of tokens that still need to be parsed
        If a grammar error occured:
            - Raises a Syntax Error with a message of where the error occured
    """
    head, *tail = tokens
    if head.tokentype_ == TokenTypes.CALL:
        return [], tokens
    return parse_function_call_parameters_loop(characters, tokens)
    



def parse_function_call(
    characters: str, 
    tokens: List['Token']
) -> Tuple['CallExpression', List['Token']]:
    """Function tries to parse a function call statement
    
    Note: 
        Follows the following grammar rules:
            1. A function call statement starts with a TokenType.CALL and 
                ends with a TokenType.CALL
            2. A function call parameter must be separated by a '|'
    
    Args:
        characters  : The characters that are being lexed, parsed, interpreted
        tokens      : List of tokens that need to be parsed
    
    Returns:
        If no errors occured:
            - A CallExpression node representing the function call
            - A list of tokens that still need to be parsed
        If a grammar error occured:
            - Raises a Syntax Error with a message of where the error occured
    """
    call_start, identifier, *tail = tokens
    if identifier.tokentype_ not in (TokenTypes.PRINT, TokenTypes.IDENTIFIER):
        generate_error_message(identifier, characters, "Expected identifier or print after call statement", True)
    
    callee              = Identifier(loc_=identifier.loc_, range_=identifier.range_, name_=identifier.value_)
    arguments, tokens   = parse_function_call_parameters(characters, tail)
    
    call_end, *tail = tokens
    
    loc_ = {"start": call_start.loc_["start"], "end": call_end.loc_["end"]}
    range_   = [call_start.range_[0], call_end.range_[1]]
    node                = CallExpression(loc_=loc_, range_=range_, arguments_=arguments, callee_=callee)
    return node, tail