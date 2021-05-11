"""
@file error_message.py
@author Nathan Houwaart (nathan.houwaart@student.hu.nl)
@brief This file contains error message functcions
@version 0.1
@date 11-05-2021
"""

from misc.token_types import *
from misc.overload import overload


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
    
    error_message       = message + "\n" + f"File <placeholder>, line {line_no_error}\n\t{invalid_chars}\n\t{' '*start_index_error+ (end_index_error-start_index_error)*'^'}"
    if raise_error:
        raise Exception(error_message)
    return error_message
