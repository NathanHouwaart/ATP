"""
@file parse_function_declaration.py
@author Nathan Houwaart (nathan.houwaart@student.hu.nl)
@brief This file contains functions to parse a function declaration
@version 0.1
@date 11-05-2021
"""

from typing import Optional, List, Tuple
from misc.node_types import *
from misc.token_types import TokenTypes, Token
from misc.error_message import generate_error_message
import parser_submodules.parse_expression as parse_expr
try     : import parser_module.parser as parser
except  : import parser as parser


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
    function_declaration_start, identifier, *tail = tokens
    if identifier.tokentype_ != TokenTypes.IDENTIFIER:
        generate_error_message(identifier, characters, "Expected identifier after function declaration", True)
    
    function_parameters, tokens = parse_function_params(characters, tail)
    function_body, tokens       = parser.parse(characters, tokens, termination_tokens=[TokenTypes.FUNCTION_DECLARATION_END])
    function_declaration_end, *tail = tokens
    
    if len(function_body) == 0:
        generate_error_message(identifier, characters, "Function body cannot be empty", True)

    loc_ = {"start": function_body[0].loc_["start"], "end": function_body[-1].loc_["end"]}
    range_   = [function_body[0].range_[0], function_body[-1].range_[1]]
    function_body               = BlockStatement(loc_=loc_, range_=range_, body_=function_body)                               # Convert the function body to a blockstatement
    
    loc_ = {"start": function_declaration_start.loc_["start"], "end": function_declaration_end.loc_["end"]}
    range_   = [function_declaration_start.range_[0], function_declaration_end.range_[1]]
    node                        = FunctionDeclaration(loc_=loc_, range_=range_, id_=identifier.value_, params_=function_parameters, body_=function_body)
    return node, tail


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
    
    param =  Identifier(loc_=head.loc_, range_=head.range_, name_=head.value_)
    params, tokens = parse_function_params(characters, tail)
    return [param] + params, tokens


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
    return_statement_start, head, *tail = tokens
    
    node, tokens = parse_expr.parse_expression(characters, [head]+tail)
    
    return_statement_end, *tail = tokens
    if return_statement_end.tokentype_ != TokenTypes.RETURN:
        generate_error_message(return_statement_end, characters, "Expected closing '⮐' after return statement", True)
    
    loc_ = {"start": return_statement_start.loc_["start"], "end": return_statement_end.loc_["end"]}
    range_   = [return_statement_start.range_[0], return_statement_end.range_[1]]
    node = ReturnStatement(loc_=loc_,range_=range_, argument_=node)
    return node, tail


