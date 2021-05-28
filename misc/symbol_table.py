"""
@file symbol_table.py
@author Nathan Houwaart (nathan.houwaart@student.hu.nl)
@brief This file contains the SymbolTable object and functions used to edit the a SymbolTable object
@version 0.1
@date 11-05-2021
"""

from misc.node_types import Node
from typing import Tuple, Callable, Optional, Dict,  Any, List
try : from token_types import *
except : from misc.token_types import *
from dataclasses import dataclass
from copy import deepcopy


@dataclass(frozen=False)
class SymbolTable:
    """
    SymbolTable class
    ...

    Attributes
    ----------
    symbols : Dict[str, Any]
        A dictionary containing symbol identifiers and their respective values
    parent: Optional['SymbolTable']
        Pointer to parent SymbolTable (if there is a parent)
    return_symbols: List[Any]
        List containing return symbols that get returned from interpret functions
    return_stop: bool
        Boolean inidcating wether a return statement was executed. No more nodes from
        that specific scope should be executed anymore
    """
    symbols : Dict[str, Any]
    parent  : Optional['SymbolTable']
    return_symbols      : List[Any]
    return_stop         : bool

def symbol_table_symbol_exists(symbol_table: SymbolTable, name: str):
    return True if symbol_table.symbols.get(name) else False

def symbol_table_set(symbol_table: SymbolTable, name: str, value: Any) -> SymbolTable:
    # symbol_table = deepcopy(symbol_table)
    symbol_table.symbols[name] = value
    return symbol_table

def symbol_table_set_list_of_arguments(symbol_table: SymbolTable, arguments: List[Tuple[str, Any]]) -> SymbolTable:
    if len(arguments) == 0: return symbol_table
    head, *tail = arguments 
    return symbol_table_set_list_of_arguments(symbol_table_set(symbol_table, head[0], head[1]), tail)

def symbol_table_get(symbol_table: SymbolTable, name: str):
    value = symbol_table.symbols.get(name,  None)
    if value == None and symbol_table.parent:
        return symbol_table_get(symbol_table.parent, name)
    return value

def symbol_table_get_and_remove(symbol_table: SymbolTable, name: str):
    value        = symbol_table_get(symbol_table, name)
    symbol_table = symbol_table_remove(symbol_table, name)
    return value, symbol_table
    
def symbol_table_remove(symbol_table: SymbolTable, name):
    # symbol_table = deepcopy(symbol_table)
    del symbol_table.symbols[name]
    return symbol_table

def symbol_table_add_return_symbol(symbol_table: SymbolTable, value: Any):
    # symbol_table = deepcopy(symbol_table)
    symbol_table.return_symbols.append(value)
    return symbol_table

def symbol_table_get_and_del_return_symbol(symbol_table: SymbolTable):
    # symbol_table = deepcopy(symbol_table)
    return_symbols = deepcopy(symbol_table.return_symbols)
    symbol_table.return_symbols.clear()
    return return_symbols, symbol_table

def symbol_table_set_return_stop(symbol_table: SymbolTable):
    # symbol_table = deepcopy(symbol_table)
    symbol_table.return_stop = True
    return symbol_table

def symbol_table_reset_return_stop(symbol_table: SymbolTable):
    # symbol_table = deepcopy(symbol_table)
    symbol_table.return_stop = False
    return symbol_table