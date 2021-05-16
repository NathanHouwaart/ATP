"""
@file parse_if_statements.py
@author Nathan Houwaart (nathan.houwaart@student.hu.nl)
@brief This file contains functions to parse an if-else statement
@version 0.1
@date 11-05-2021
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# print(sys.modules.keys())

from misc.node_types import *
from misc.token_types import *
from typing import Optional, List, Tuple
from misc.error_message import generate_error_message

try     : import parser_module.parser as parser
except  : import parser as parser_
import parser_submodules.parse_expression as parse_expr
 

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
    test, tokens = parse_expr.parse_expression(characters, tokens)
    
    head, *tail = tokens
    if head.tokentype_ != TokenTypes.INDENTATION:
        generate_error_message(head, characters, "Expected '––>' after if statement", True)

    head, *tail = tail
    if head.tokentype_ != TokenTypes.NEW_LINE:
        generate_error_message(head, characters, "Expected new line after if statement", True)
    return test, tail



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
    valid_termination_characters = [TokenTypes.IF_STATEMENT_END, TokenTypes.ELSE, TokenTypes.ELSE_IF]
    if_statement_start, *tail = tokens
    test, tokens = parse_if_statement_test(characters, tail)
    body, tokens = parser.parse(characters, tokens, termination_tokens=valid_termination_characters)
    termination_token, *tail = tokens
    
    if len(body) == 0:
        generate_error_message(termination_token, characters, "If statement body cannot be empty", True)
    if termination_token.tokentype_ not in valid_termination_characters:
        generate_error_message(termination_token, characters, "Expected '¿', '⁈', or '⁇' after if statement", True)
        
    if termination_token.tokentype_ == TokenTypes.ELSE_IF:
        alternative, tokens = parse_if_statement(characters, tokens)

        loc_        = {"start": body[0].loc_["start"], "end": body[-1].loc_["end"]}
        range_      = [body[0].range_[0], body[-1].range_[1]]
        consequent_ = BlockStatement(loc_=loc_, range_=range_, body_=body)

        loc_    = {"start": if_statement_start.loc_["start"], "end": alternative.loc_["end"]}
        range_   = [if_statement_start.range_[0], alternative.range_[1]]
        return IfStatement(loc_=loc_, range_=range_, test_=test, consequent_=consequent_, alternate_=alternative), tokens
    elif termination_token.tokentype_ == TokenTypes.ELSE:
        head, *tail = tail
        if head.tokentype_ != TokenTypes.INDENTATION:
            generate_error_message(head, characters, "Expected '––>' statement after else block", True)
        alternative, tokens = parser.parse(characters, tail, termination_tokens=[TokenTypes.IF_STATEMENT_END])
        if_statement_end, *tail = tokens
        
        if if_statement_end.tokentype_ != TokenTypes.IF_STATEMENT_END:
            generate_error_message(if_statement_end, characters, "Expected '¿' after if statement end", True)
        if len(alternative) == 0:
            generate_error_message(if_statement_end, characters, "Else statement body cannot be empty", True)
        
        loc_        = {"start": body[0].loc_["start"], "end": body[-1].loc_["end"]}
        range_      = [body[0].range_[0], body[-1].range_[1]]
        consequent_ = BlockStatement(loc_=loc_, range_=range_, body_=body)
        
        loc_        = {"start": alternative[0].loc_["start"], "end": alternative[-1].loc_["end"]}
        range_      = [alternative[0].range_[0], alternative[-1].range_[1]]
        alternative = BlockStatement(loc_=loc_, range_=range_, body_=alternative)
        loc_    = {"start": if_statement_start.loc_["start"], "end": if_statement_end.loc_["end"]}
        range_   = [if_statement_start.range_[0], if_statement_end.range_[1]]
        return IfStatement(loc_=loc_, range_=range_, test_=test, consequent_=consequent_, alternate_=alternative), tail
    
    loc_        = {"start": body[0].loc_["start"], "end": body[-1].loc_["end"]}
    range_      = [body[0].range_[0], body[-1].range_[1]]
    consequent_ = BlockStatement(loc_=loc_, range_=range_, body_=body)

    loc_    = {"start": if_statement_start.loc_["start"], "end": termination_token.loc_["end"]}
    range_   = [if_statement_start.range_[0], termination_token.range_[1]]
    return IfStatement(loc_=loc_, range_=range_, test_=test, consequent_=consequent_, alternate_=[]), tail