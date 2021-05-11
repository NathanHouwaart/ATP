"""
@file parse_expression.py
@author Nathan Houwaart (nathan.houwaart@student.hu.nl)
@brief This file contains functions to parse expressions
@version 0.1
@date 11-05-2021
"""
import sys
import os

from misc.node_types import *
from misc.token_types import TokenTypes, Token
from misc.error_message import generate_error_message
from typing import Optional, List, Tuple
import parser_modules.parse_function_call

def parse_operand(
    characters : str,
    tokens : List['Token']
) -> Optional[Tuple['Node', List['Token']]]:
    """
    Function parses an operand for an expression
    
    Rules:
        - If the operand is either a TokenTypes.PLUS or TokenTypes.MINUS, a UnaryExpression node is created
        - If the operand is either a TokenTypes.INT or TokenTypes.Float, a Literal node is created
        - If the operand is a TokenTypes.CALL, a FunctionDeclaration node is created
        - If the operand is a TokenTypes.IDENTIFIER, an Identifier node is created
        - If the operand is a TokenTypes.LEFT_PARENTHESIES, a new BinaryExpression node is created
            - After the creation of a new BinaryExpression node, a TokenTypes.RIGHT_PARENTHESIES is required 
    
    Args: 
        tokens: The tokens that need to be parsed
        
    Returns:
        If no error occurs:
            - A Node containing the found operand 
            - The leftover tokens that stil need to be parsed
        If no operand was found:
            returns None
    """
    head, *tail = tokens
    
    if head.tokentype_ in (TokenTypes.PLUS, TokenTypes.MINUS):
        node, tail = parse_operand(characters, tail)
        return UnaryExpression(loc_={}, range_=[], operator_=head.tokentype_, argument_=node), tail
    if head.tokentype_ in (TokenTypes.INT, TokenTypes.FLOAT):
        return Literal(loc_={}, range_=[], value_=int(head.value_), raw_=head.value_), tail
    if head.tokentype_ == TokenTypes.CALL:
        result, tokens = parser_modules.parse_function_call.parse_function_call(characters, tail) #TODO: characters meegeven
        return result, tokens
    if head.tokentype_ == TokenTypes.IDENTIFIER: 
        return Identifier(loc_=head.loc_, range_=head.range_, name_=head.value_), tail
    if head.tokentype_ == TokenTypes.LEFT_PARENTHESIES:
        node, tokens = parse_expression(characters, tail)
        head, *tail = tokens
        if head.tokentype_ != TokenTypes.RIGHT_PARENTHESIES:
            generate_error_message(head, characters, "Missing right parenthesies", True)
        return node, tail
    
    generate_error_message(head, characters, "Error parsing operand", True)
    

def loop(
    characters: str,
    node: 'Node', 
    tokens: str, 
    token_types: List['TokenTypes']
) -> Tuple['Node', List['Token']]:
    """Function tries to recursively parse a binary expression.
    Function recurses as long as the found 'operator' is in the provided token_types.
    
    Note:
        Function does nothing when the 'operator' token is not present in the token_type list
        In the expression 1+2, the 'operator' token is '+'
        In the expression 1, the 'operator' token can by anything line "eof, new_line, space, etc"
        
    Args:
        characters          : Characters that are being lexed, parsed and interpreted
        node                : Left node for the binary expression 
        tokens              : Tokens that need to be parsed
        token_types         : Recurse the binary expression as long as the provided operands are is in this list

    Returns:
        If no errors occured:
            - A node containing the parsed expression
            - The leftover tokens that stil need to be parsed
        If a grammar error occured:
            Raises a Syntax Error with a message of where the error occured
    """
    head, *tail = tokens
    if head.tokentype_ in token_types:
        right, tokens = parse_expression_mul_divide(characters, tail)
        node = BinaryExpression(loc_={}, range_=[], operator_=head.tokentype_, left_=node, right_=right)
        return loop(characters, node, tokens, token_types)
    return node, tokens


def parse_expression_mul_divide(
    characters: str,
    tokens: List['Token']
) -> Tuple['Node', List['Token']]:
    """Function is used to parse an operand node and then looks recursively 
    for multiply and divide tokens to create a binary expression
    
    Args:
        characters          : Characters that are being lexed, parsed and interpreted
        tokens              : Tokens that need to be parsed

    Returns:
        If no errors occured:
            - A node containing the parsed expression
            - The leftover tokens that stil need to be parsed
        If a grammar error occured:
            Raises a Syntax Error with a message of where the error occured
    """
    node, tokens = parse_operand(characters, tokens)
    node, tokens = loop(characters, node, tokens, (TokenTypes.MULTIPLY, TokenTypes.DIVIDE))
    return node, tokens

def parse_expression(
    characters: str,
    tokens: List['Token']
) -> Tuple['Node', List['Token']]:
    """Function is used to parse an expression statement
    
    Note:
        Expression follows basic math rules:
            1. Parentesies and unary operators take most priority
            2. Multiply and Divide take second most priority
            3. Add and Subtract take least most priority
        
    Args:
        characters          : Characters that are being lexed, parsed and interpreted
        tokens              : Tokens that need to be parsed

    Returns:
        If no errors occured:
            - A node containing the parsed expression
            - The leftover tokens that stil need to be parsed
        If a grammar error occured:
            Raises a Syntax Error with a message of where the error occured
    """
    expression, tokens = parse_expression_mul_divide(characters, tokens)
    expression, tokens = loop(characters, expression, tokens, (TokenTypes.MINUS, TokenTypes.PLUS))
    return expression, tokens