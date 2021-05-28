"""
@file error_message.py
@author Nathan Houwaart (nathan.houwaart@student.hu.nl)
@brief This file contains functions to display an error message
@version 0.1
@date 11-05-2021
"""

from misc.token_types import *
from misc.overload import overload
import misc.node_types as node_types

@overload((int, int, str, str, bool))
def generate_error_message(line_no: int, index: int, characters: str, message: str, raise_error:bool):
    line                = characters.split("\n")[line_no-1]
    error_message       = message + "\n" + f"File <placeholder>, line {line_no}\n\t{line}\n\t{' '*(index+1) + '^^^^'}"
    if raise_error:
        raise Exception(error_message)
    return error_message


@overload((Token, str, str, bool))
def generate_error_message(token: Token, characters: str, message: str, raise_error:bool):
    line_no_error       = token.loc_["start"]["line"]
    start_index_error   = token.loc_["start"]["index"]
    end_index_error     = token.loc_["end"]["index"]
    invalid_chars       = characters.split("\n")[token.loc_["start"]["line"]-1]
    error_message       = message + "\n" + f"File <placeholder>, line {line_no_error}\n\t{invalid_chars}\n\t{(' '*start_index_error)+ (end_index_error-start_index_error)*'^'}"
    if raise_error:
        raise Exception(error_message)
    return error_message


@overload((node_types.FunctionDeclaration, node_types.FunctionDeclaration, str, str, bool))
def generate_error_message(func_1: node_types.Node, func_2:node_types.Node, characters: str, message: str, raise_error: bool):
    func_1_line_no_error       = func_1.loc_["start"]["line"]
    func_1_start_index_error   = func_1.loc_["start"]["index"]
    func_1_invalid_chars       = characters.split("\n")[func_1_line_no_error-1]
    
    func_2_line_no_error       = func_2.loc_["start"]["line"]
    func_2_start_index_error   = func_2.loc_["start"]["index"]
    func_2_invalid_chars       = characters.split("\n")[func_2_line_no_error-1]  

    if func_1_line_no_error < func_2_line_no_error:
        error_message       = message + "\n" + f"File <placeholder>, line {func_1_line_no_error}"
        error_message       += f"\n\t{func_1_invalid_chars}\n\t{' '*func_1_start_index_error+ len(func_1_invalid_chars)*'^'}\n"
        error_message       +="\n" + f"File <placeholder>, line {func_2_line_no_error}"
        error_message       += f"\n\t{func_2_invalid_chars}\n\t{' '*func_2_start_index_error+ len(func_2_invalid_chars)*'^'}\n"
    else:
        error_message       = message + "\n" + f"File <placeholder>, line {func_2_line_no_error}"
        error_message       += f"\n\t{func_2_invalid_chars}\n\t{' '*func_2_start_index_error+ len(func_2_invalid_chars)*'^'}\n"
        error_message       +="\n" + f"File <placeholder>, line {func_1_line_no_error}"
        error_message       += f"\n\t{func_1_invalid_chars}\n\t{' '*func_1_start_index_error+ len(func_1_invalid_chars)*'^'}\n"
    if raise_error:
        raise Exception(error_message)
    return error_message

@overload((node_types.Literal, str, str, bool))
def generate_error_message(node: node_types.Literal, characters: str, message: str, raise_error: bool):
    line_no_error       = node.loc_["start"]["line"]
    start_index_error   = node.loc_["start"]["index"]
    invalid_chars       = characters.split("\n")[line_no_error-1]
    
    error_message       = message + "\n" + f"File <placeholder>, line {line_no_error}"
    error_message       += f"\n\t{invalid_chars}\n\t{' '*start_index_error+ len(invalid_chars)*'^'}\n"
    
    if raise_error:
        raise Exception(error_message)
    return error_message

@overload((node_types.Identifier, str, str, bool))
def generate_error_message(node: node_types.Identifier, characters: str, message: str, raise_error: bool):
    line_no_error       = node.loc_["start"]["line"]
    start_index_error   = node.loc_["start"]["index"]
    end_index_error     = node.loc_["end"]["index"]
    invalid_chars       = characters.split("\n")[line_no_error-1]
    
    error_message       = message + "\n" + f"File <placeholder>, line {line_no_error}\n\t{invalid_chars}\n\t{' '*start_index_error+ (end_index_error-start_index_error)*'^'}"
    if raise_error:
        raise Exception(error_message)
    return error_message
