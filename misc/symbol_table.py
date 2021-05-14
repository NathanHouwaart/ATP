from typing import Tuple, Callable, Optional, Dict,  Any, List
try : from token_types import *
except : from misc.token_types import *
from dataclasses import dataclass
from copy import deepcopy

@dataclass(frozen=True)
class ReturnObject:
    return_values : List[any]
    
@dataclass(frozen=False)
class SymbolTable:
    symbols : Dict
    parent  : Optional['SymbolTable']
    return_symbols      : List
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