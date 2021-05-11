"""
@file parse_function_declaration.py
@author Nathan Houwaart (nathan.houwaart@student.hu.nl)
@brief This file contains functions to parse a function declaration
@version 0.1
@date 11-05-2021
"""

import sys
import os

from typing import Optional, List, Tuple
from misc.node_types import *
from misc.token_types import TokenTypes, Token
from misc.error_message import generate_error_message
import parser_modules.parse_expression
import parser_p

def parse_function_declaration():
    pass
def parse_function_params():
    pass
def parse_return_statement():
    pass

# def parse_function_dec
def parse_function_declaration(
    characters:str, 
    tokens: List['Token']
) -> Tuple['FunctionDeclaration', List['Token']]:
    """ Function tries to parse a function declaration
    
    Note: 
        Follows the following grammar rules:
            1. A function declaration needs to be followed by a TokenType.IDENTIFIER
            2. After the identifier, get function parameters (if there are any)
            3. Finally, parse the function body just like a normal piece of code, look for a 
                TokenType.FUNCTION_DECLARATION_END token to stop parsing at the end of the function
    
    Args:
        characters  : The characters that are being lexed, parsed, interpreted
        tokens      : List of tokens that need to be parsed
    
    Returns:
        If no errors occured:
            - A FunctionDeclaration node 
            - A list of tokens that still need to be parsed
        If a grammar error occured:
            - Raises a Syntax Error with a message of where the error occured
    """
    head, *tail = tokens
    if head.tokentype_ != TokenTypes.IDENTIFIER:
        generate_error_message(head, characters, "Expected identifier after function declaration", True)
    
    function_parameters, tokens = parse_function_params(characters, tail)
    function_body, tokens       = parser_p.parse(characters, tokens, termination_tokens=[TokenTypes.FUNCTION_DECLARATION_END])   
    function_body               = BlockStatement(loc_={}, range_=[], body_=function_body)                               # Convert the function body to a blockstatement
    node                        = FunctionDeclaration(loc_={}, range_=[], id_=head.value_, params_=function_parameters, body_=function_body)
    return node, tokens


def parse_function_params(
    characters: str, 
    tokens: List['Token']
) -> Tuple[List['Node'], List['Token']]:
    """ Function tries to parse function parameters
    
    Note: 
        Follows the following sequence of grammar rules:
            1. A function body starts when the TokenType.INDENTATION is found
                1a. This token must be followed by a TokenType.NEW_LINE
            2. If a newline is found before a TokenType.INDENTATION, raise an exception
            3. Check for a TokenType.SEPARATOR, raise an exception if not found
            4. Check for a TokenType.PARAMETER, raise an exception if not found
            5. Check for an identifier, raise an exception if not found
            6. Gerenare Identifier Node and recurse
    
    Args:
        characters  : The characters that are being lexed, parsed, interpreted
        tokens      : List of tokens that need to be parsed
    
    Returns:
        If no errors occured:
            - A List of identifier nodes which make up the function parameters 
            - A list of tokens that still need to be parsed
        If a grammar error occured:
            - Raises a Syntax Error with a message of where the error occured
    """
    head, *tail = tokens
    if head.tokentype_ == TokenTypes.INDENTATION :
        head, *tail = tail
        if head.tokentype_ != TokenTypes.NEW_LINE:
            generate_error_message(head, characters, "Expected newline '––>' after function declaration", True)
        return [], tail
    if head.tokentype_ == TokenTypes.NEW_LINE:
        generate_error_message(head, characters, "Expected '––>' after function declaration", True)
    if head.tokentype_ != TokenTypes.SEPARATOR:
        generate_error_message(head, characters, "Expected '|' or '––>' after function parameter declaration", True)
    
    head, *tail = tail
    if head.tokentype_ != TokenTypes.PARAMETER:
        generate_error_message(head, characters, "Expected 'parameter declaration' after function separator", True)
    head, *tail = tail
    if head.tokentype_ != TokenTypes.IDENTIFIER:
        generate_error_message(head, characters, "Expected 'identifier' after function parameter declaration", True)
    
    param =  Identifier(loc_={}, range_=[], name_=head.value_)
    params, tokens = parse_function_params(characters, tail)
    return [param] + params, tokens


parse_function_params
def parse_return_statement(
    characters: str, 
    tokens: List['Token']
) -> Tuple['ReturnStatement', List['Token']]:
    """Function tries to parse a return statement 
    
    Note: 
        Follows the following grammar rules:
            1. A returnstatement must be followed by an expression
    
    Args:
        characters  : The characters that are being lexed, parsed, interpreted
        tokens      : List of tokens that need to be parsed
    
    Returns:
        If no errors occured:
            - A ReturnStatement node 
            - A list of tokens that still need to be parsed
        If a grammar error occured:
            - Raises a Syntax Error with a message of where the error occured
    """
    head, *_ = tokens

    if head.tokentype_ not in (TokenTypes.CALL,TokenTypes.IDENTIFIER, TokenTypes.MINUS, TokenTypes.PLUS, TokenTypes.INT, TokenTypes.FLOAT, TokenTypes.LEFT_PARENTHESIES):
        generate_error_message(head, characters, "Expected expression after 'return' statement", True)
    
    node, tokens = parser_modules.parse_expression.parse_expression(characters, tokens)
    node = ReturnStatement(loc_={},range_=[], argument_=node)
    return node, tokens


