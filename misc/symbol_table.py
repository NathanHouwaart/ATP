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
from enum import Enum


class SymbolType(Enum):
    FUNCTION = 1
    VARIABLE = 2
    ARGUMENT = 3
    RETURN   = 4
    STACK    = 5


@dataclass(frozen=False)
class Symbol:
    symbol_name:            str
    symbol_type:            SymbolType
   
@dataclass(frozen=False)
class FunctionSymbol(Symbol):
    no_args:  int
    
@dataclass(frozen=False)
class VairableSymbol(Symbol):
    symbol_register:        int


@dataclass(frozen=False)
class SymbolTable:
    """
    SymbolTable class
    ...

    Attributes
    ----------
    symbols : Dict[str, Symbol]
        A dictionary containing symbol identifiers and their respective values or registers
    parent: Optional['SymbolTable']
        Pointer to parent SymbolTable (if there is a parent)
    return_symbols: List[Any]
        List containing return symbols that get returned from interpret functions
    return_stop: bool
        Boolean inidcating wether a return statement was executed. No more nodes from
        that specific scope should be executed anymore
    """
    
    symbols             : Dict[str, Symbol]
    parent              : Optional['SymbolTable']
    return_symbols      : List[Any]
    return_stop         : bool
    stack_variables     : int


def symbol_table_symbol_exists(symbol_table: SymbolTable, symbol_name: str) -> bool:
    """
    Checks if a symbol exists in the symbol table
    """
    return True if symbol_table.symbols.get(symbol_name) else False


def symbol_table_set(symbol_table: SymbolTable, symbol_name: str, symbol: Symbol) -> SymbolTable:
    """
    Set a symbol in the symbol table
    """
    symbol_table.symbols[symbol_name] = symbol
    return symbol_table


def symbol_table_get(symbol_table: SymbolTable, symbol_name: str) -> Symbol:
    """
    Get a symbol from the symbol table. Eiter in its symbol table or its parent. Return None if not found
    """
    symbol = symbol_table.symbols.get(symbol_name,  None)
    if symbol == None and symbol_table.parent:
        return symbol_table_get(symbol_table.parent, symbol_name)
    return symbol


def symbol_table_get_and_remove(symbol_table: SymbolTable, symbol_name: str) -> Tuple[Symbol, SymbolTable]:
    """
    Get a symbol and remove it from the symbol table
    """
    symbol  = symbol_table_get(symbol_table, symbol_name)
    symbol_table = symbol_table_remove(symbol_table, symbol_name)
    return symbol, symbol_table


def symbol_table_remove(symbol_table: SymbolTable, symbol_name: str):
    """
    Remove a symbol from the symbol table
    """
    del symbol_table.symbols[symbol_name]
    return symbol_table


def symbol_table_add_return_symbol(symbol_table: SymbolTable, value: Any):
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

def symbol_table_add_stack_variable_amt(symbol_table: SymbolTable):
    # symbol_table = deepcopy(symbol_table)
    symbol_table.stack_variables += 1
    return symbol_table

def symbol_table_get_stack_variable_amt(symbol_table: SymbolTable):
    # symbol_table = deepcopy(symbol_table)
    return symbol_table.stack_variables