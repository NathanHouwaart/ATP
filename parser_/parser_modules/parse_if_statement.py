"""
@file parse_if_statements.py
@author Nathan Houwaart (nathan.houwaart@student.hu.nl)
@brief This file contains functions to parse an if-else statement
@version 0.1
@date 11-05-2021
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append('.')
sys.path.append('../')
sys.path.append('../helper')

from misc.node_types import *
from misc.token_types import *
from typing import Optional, List, Tuple
from misc.error_message import generate_error_message
import parser_ as parser
import parser_modules.parse_expression as parse_expr
 
def parse_binary_test(
    characters: str, 
    tokens: List['Token']
) -> Tuple['BinaryExpression', List['Token']]:
    """ Function tries to parse a binary test for an if statement
    
    Note: 
        A binary expression must consist:
            1. A left expression
            2. An operator
            3. A right expression
    Args:
        characters  : The characters that are being lexed, parsed, interpreted
        tokens      : List of tokens that need to be parsed
    
    Returns:
        If no errors occured:
            - A BinaryExpression node 
            - A list of tokens that still need to be parsed
        If a grammar error occured:
            - Raises a Syntax Error with a message of where the error occured
    """
    head, *tail = tokens
    if head.tokentype_ not in (TokenTypes.IDENTIFIER, TokenTypes.FLOAT, TokenTypes.INT):
        generate_error_message(head, characters, "Expected identifier or literal in if statement", True)
    
    left, tokens = parse_expr.parse_expression(characters, tokens)
    head, *tail = tokens
    if head.tokentype_ not in (TokenTypes.GREATER_THAN, TokenTypes.SMALLER_THAN, TokenTypes.IS_EQUAL):
        generate_error_message(head, characters, "Expected identifier or literal in if statement", True)
    right, tokens = parse_expr.parse_expression(characters, tail)
    test = BinaryExpression(loc_={}, range_=[], operator_=head.tokentype_, left_=left, right_=right)
    return test, tokens

def parse_if_statement_loop(node, characters, tokens):
    """
    Functies tries to parse multiple if statement tests
    
    Note: 
        The following grammar rules apply:
            1. Two expressions must be separated by an TokenType.OR or TokenType.AND token

    Args:
        characters  : The characters that are being lexed, parsed, interpreted
        tokens      : List of tokens that need to be parsed
    
    Returns:
        If no errors occured:
            - A BinaryExpression node 
            - A list of tokens that still need to be parsed
        If a grammar error occured:
            - Raises a Syntax Error with a message of where the error occured
    """
    head, *tail = tokens
    if head.tokentype_ in (TokenTypes.AND, TokenTypes.OR):
        right, tokens = parse_binary_test(characters, tail)
        node = BinaryExpression(loc_={}, range_=[], operator_=head.tokentype_, left_=node, right_=right)
    return node, tokens

def parse_if_statement_test(
    characters:str, 
    tokens: List['Token']
) -> Tuple['BinaryExpression', List['Token']]:
    """
    Functies parses a test for an if-statement
    
    Note: 
        The following grammar rules apply:
            1. An if statement must be followed by a binary expression 
            2. The last if statement test must be followed by an '––>'
            3. An '––>' must be followed by a newline

    Args:
        characters  : The characters that are being lexed, parsed, interpreted
        tokens      : List of tokens that need to be parsed
    
    Returns:
        If no errors occured:
            - A BinaryExpression node 
            - A list of tokens that still need to be parsed
        If a grammar error occured:
            - Raises a Syntax Error with a message of where the error occured
    """
    node, tokens = parse_binary_test(characters, tokens)
    node, tokens = parse_if_statement_loop(node, characters, tokens)
    
    head, *tail = tokens
    if head.tokentype_ != TokenTypes.INDENTATION:
        generate_error_message(head, characters, "Expected '––>' after if statement", True)

    head, *tail = tail
    if head.tokentype_ != TokenTypes.NEW_LINE:
        generate_error_message(head, characters, "Expected new line after if statement", True)
    return node, tail


def trim_token_list(
    tokens: List['Token'], 
    trim: Tuple['TokenTypes']
) -> list['Token']:
    """ Function trims the provided token list by removing the instances found in trim untill another non included token is found
    
    Args:
        tokens      : List of tokens that need to be trimmed
        trim        : Trim these TokenTypes from the from of the list
    Returns:
        - A list containing the trimmed tokens
    """
    head, *tail = tokens
    if head.tokentype_ not in trim:
        return tokens
    return trim_token_list(tail, trim)


def parse_if_statement(
    characters: str, 
    tokens: List['Token']
) -> Tuple['IfStatement', List['Token']]:
    """
    Function parses an if statement 
    
    Note: 
        The following grammar rules apply:
            1. An if statement starts with a TokenType.IF token
            2. An if statement, elif statement and else statement must each end with a TokenType.IF_STATEMENT_END 
            3. An if statement must contain a test (binaryexpression)
            4. Parse an if statement body just like normal code
                4a. Look out for a TokenType.IF_STATEMENT_END to stop parsing the function body
            5. If a TokenTypes.ELSE_IF token is found, recurse this function

    Args:
        characters  : The characters that are being lexed, parsed, interpreted
        tokens      : List of tokens that need to be parsed
    
    Returns:
        If no errors occured:
            - An IfStatement node 
            - A list of tokens that still need to be parsed
        If a grammar error occured:
            - Raises a Syntax Error with a message of where the error occured
    """
    if_statement_start, head, *tail = tokens
    if head.tokentype_ == TokenTypes.INDENTATION:
        return [], tail
    test, tokens = parse_if_statement_test(characters, [head]+tail)
    body, tokens = parser.parse(characters, tokens, termination_tokens=[TokenTypes.IF_STATEMENT_END])
    if_statement_end, *tail = tokens
    
    if len(body) == 0:
        generate_error_message(if_statement_end, characters, "If statement body cannot be empty", True)
    
    head, *tail = trim_token_list(tail, [TokenTypes.TAB, TokenTypes.NEW_LINE])

    if head.tokentype_ == TokenTypes.ELSE_IF:
        alternative, tokens = parse_if_statement(characters, tail)
        return IfStatement(loc_={}, range_=[], test_=test, consequent_=BlockStatement(loc_={}, range_=[], body_=body), alternate_=alternative), tokens
    if head.tokentype_ == TokenTypes.ELSE:
        head, *tail = tail
        if head.tokentype_ != TokenTypes.INDENTATION:
            generate_error_message(head, characters, "Expected '––>' statement after else block", True)
        alternative, tokens = parser.parse(characters, tail, termination_tokens=[TokenTypes.IF_STATEMENT_END])
        return IfStatement(loc_={}, range_=[], test_=test, consequent_=BlockStatement(loc_={}, range_=[], body_=body), alternate_=alternative), tokens
    
    loc_        = {"start": body[0].loc_["start"], "end": body[-1].loc_["end"]}
    range_      = [body[0].range_[0], body[-1].range_[1]]
    consequent_ = BlockStatement(loc_=loc_, range_=range_, body_=body)

    loc_    = {"start": if_statement_start.loc_["start"], "end": if_statement_end.loc_["end"]}
    range_   = [if_statement_start.range_[0], if_statement_end.range_[1]]
    return IfStatement(loc_=loc_, range_=range_, test_=test, consequent_=consequent_, alternate_=[]), [head]+tail