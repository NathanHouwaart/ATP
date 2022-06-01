from ast import Return, literal_eval, operator
from ctypes.wintypes import PUSHORT
from inspect import stack
from pyclbr import Function
import sys
import os
import time
from itertools import islice
from tkinter import Variable


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Set, Tuple, Callable, Optional, Dict, List
from lexer_module.lexer import lex, search_match
from parser_module.parser import parse
from misc.token_types import *
from misc.node_types import *
from misc.error_message import generate_error_message
from misc.symbol_table import *

def get_attribute(method_name, default):
    if method_name in globals():
        return globals()[method_name]
    return default

def no_graph_method(code, node, symbol_table, inp, current_scope):
    print("no compile method for node type", type(node))
    return symbol_table

def graph_VariableDeclaration(code, node: VariableDeclaration, symbol_table: SymbolTable, inp, current_scope):
    symbol_table = graph_loop(code, [node.init_], symbol_table, inp, current_scope)
    return symbol_table

def graph_Literal(code, node: Literal, symbol_table: SymbolTable, inp, current_scope):
    print(node)
    exit()
    return symbol_table

def graph_loop(code, program_nodes: List[Node], symbol_table: SymbolTable, inp : List[Any], current_scope) -> SymbolTable:
    if len(program_nodes) == 0 or symbol_table.return_stop == True:
        return symbol_table
    
    node, *tail = program_nodes   
    node_type = type(node)

    method_name  = f"graph_{type(node).__name__}"
    method       = get_attribute(method_name, no_graph_method)
    symbol_table = method(code, node, symbol_table, inp, current_scope)
    
    return graph_loop(code, tail, symbol_table, inp, current_scope)


def graph(code, program: Program):
    symbol_table = SymbolTable(symbols={}, parent=None, return_symbols=[], return_stop=False, stack_variables=0)
    symbol_table = symbol_table_set(symbol_table, "🖨", FunctionSymbol("__aeabi_idiv", SymbolType.FUNCTION, 1))
    # cm0_preamble()   
    inp = []
    graph_loop(code, program.body_, symbol_table, inp, [])
    # cm0_postamble()
    print()    


if __name__ == '__main__':
    # if len(sys.argv) < 2:
    #     print("Expected filename")
    #     exit()

    with open("D:\\Nathan\\Bestanden\\ATP\\testfile.txt", "rb") as f:
        code = f.read().decode("utf-8")  
        
    # with open(sys.argv[1], "rb") as f:
    #     code = f.read().decode("utf-8")  
    time_start = time.time()
    lexed = lex(code, search_match, TokenExpressions)
    tokens = list(filter(lambda token: token.tokentype_ != TokenTypes.NONE, lexed))

    parsed, eof_token = parse(code, tokens)
    program = Program(loc_={'start': {'line': 1, 'index': 0}, "end":{"line":tokens[-1].loc_["start"]["line"], "index":tokens[-1].loc_["start"]["index"]}}, range_=[0, len(code)], body_=parsed)
    
    with open("ast_to_interpret.json", "wb") as f:
        f.write(program.jsonify().encode("utf-8"))
    
    
    result = graph(code, program)
    
    time_stop = time.time()
    print("program finished in", round(time_stop-time_start, 5), "s")
    