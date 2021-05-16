import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Tuple, Callable, Optional, Dict, List
from lexer_module.lexer import lex, search_match
from parser_module.parser import parse
from misc.token_types import *
from misc.node_types import *
from misc.error_message import generate_error_message
from misc.symbol_table import *

def interpret_CallExpression(code: str, node: CallExpression, symbol_table: SymbolTable):
    callee, symbol_table = symbol_table_get_and_del_return_symbol(interpret_Identifier(code, node.callee_, symbol_table))
    result, symbol_table = symbol_table_get_and_del_return_symbol(interpret_loop(code, node.arguments_, symbol_table))

    if callee[0] == print: print(*result); return symbol_table
    argument_names  = [argument.name_ for argument in callee[0].params_]
    arguments       = list(zip(argument_names, result))

    function_symbol_table = SymbolTable(symbols={}, parent=symbol_table, return_symbols=[], return_stop=False)
    function_symbol_table = symbol_table_set_list_of_arguments(function_symbol_table, arguments)
    function_symbol_table = interpret_loop(code, [callee[0].body_], function_symbol_table)
    
    result, function_symbol_table = symbol_table_get_and_del_return_symbol(function_symbol_table)
    symbol_table = symbol_table_add_return_symbol(symbol_table, *result)
    return symbol_table
    

def interpret_Identifier(code: str, node: Identifier, symbol_table: SymbolTable):
    value = symbol_table_get(symbol_table, node.name_)
    if value == None: generate_error_message(node, code, f"{node.name_} is not defined", True)
    return symbol_table_add_return_symbol(symbol_table, value)

def interpret_VariableDeclaration(code: str, node: VariableDeclaration, symbol_table: SymbolTable):
    symbol_table        = interpret_loop(code, [node.init_], symbol_table)
    value, symbol_table = symbol_table_get_and_del_return_symbol(symbol_table)
    return symbol_table_set(symbol_table, node.id_, *value)

def interpret_BinaryExpression(code: str, node: BinaryExpression, symbol_table: SymbolTable):
    operator = node.operator_
    
    left , symbol_table = symbol_table_get_and_del_return_symbol(interpret_loop(code, [node.left_], symbol_table))
    right, symbol_table = symbol_table_get_and_del_return_symbol(interpret_loop(code, [node.right_], symbol_table))
    left, right = left[0], right[0]
   
    if   operator == TokenTypes.PLUS          : result = left + right
    elif operator == TokenTypes.MINUS         : result = left - right
    elif operator == TokenTypes.DIVIDE        : result = left / right
    elif operator == TokenTypes.MULTIPLY      : result = left * right
    elif operator == TokenTypes.IS_EQUAL      : result = left == right
    elif operator == TokenTypes.GREATER_THAN  : result = left > right
    elif operator == TokenTypes.SMALLER_THAN  : result = left < right
    elif operator == TokenTypes.AND            : result = left and right
    elif operator == TokenTypes.OR           : result = left or right
    
    return symbol_table_add_return_symbol(symbol_table, result)


def interpret_IfStatement(code: str, node: IfStatement, symbol_table: SymbolTable):
    test_result, symbol_table = symbol_table_get_and_del_return_symbol(interpret_loop(code, [node.test_], symbol_table))
    if test_result[0]:
        return interpret_loop(code, [node.consequent_], symbol_table)
    return interpret_loop(code, [node.alternate_], symbol_table)  if node.alternate_ else symbol_table

def interpret_Literal(code: str, node: Literal, symbol_table: SymbolTable):
    return symbol_table_add_return_symbol(symbol_table, node.value_)
    
def no_interpret_method(code: str, node: Node, symbol_table: SymbolTable):
    print("no interpret method for node type", type(node))
    return symbol_table

def interpret_FunctionDeclaration(code: str, node: Node, symbol_table: SymbolTable):
    if symbol_table_symbol_exists(symbol_table, node.id_):
        generate_error_message(node, symbol_table.symbols[node.id_], code, "Runtime Error, found duplicate function identifier", True)
    return symbol_table_set(symbol_table, node.id_, node)


def get_attribute(method_name, default):
    if method_name in globals():
        return globals()[method_name]
    return default

def interpret_UnaryExpression(code: str, node: Node, symbol_table: SymbolTable):
    symbol_table            = interpret_loop(code, [node.argument_], symbol_table)
    number, symbol_table    = symbol_table_get_and_del_return_symbol(symbol_table)
    number = number[0]
    if node.operator_ == TokenTypes.MINUS:
        number = number * -1
    return symbol_table_add_return_symbol(symbol_table, number)

def interpret_ReturnStatement(code: str, node: ReturnStatement, symbol_table: SymbolTable):
    symbol_table = interpret_loop(code, [node.argument_], symbol_table)
    symbol_table = symbol_table_set_return_stop(symbol_table)
    return symbol_table

def interpret_BlockStatement(code: str, node: BlockStatement, symbol_table: SymbolTable):
    return interpret_loop(code, node.body_, symbol_table)

def interpret_loop(code, program_nodes: List[Node], symbol_table: SymbolTable) -> SymbolTable:
    if len(program_nodes) == 0 or symbol_table.return_stop == True:
        return symbol_table
    
    node, *tail = program_nodes
    node_type = type(node)
    
    method_name  = f"interpret_{type(node).__name__}"
    method       = get_attribute(method_name, no_interpret_method)
    symbol_table = method(code, node, symbol_table)
    
    return interpret_loop(code, tail, symbol_table)


def interpret(code, program: Program):
    symbol_table = SymbolTable(symbols={}, parent=None, return_symbols=[], return_stop=False)
    symbol_table = symbol_table_set(symbol_table, "🖨", print)
    return interpret_loop(code, program.body_, symbol_table)


if __name__ == '__main__':
    # if len(sys.argv) < 2:
    #     print("Expected filename")
    #     exit()

    # with open(sys.argv[0], "rb") as f:
    #     code = f.read().decode("utf-8")
    
    with open("C:\\Users\\Nathan\\Documents\\ATP\\tests\\code_samples\\valid\\if_statements\\if_statement_two_expressions_and.txt", "rb") as f:
        code = f.read().decode("utf-8")
    


    lexed = lex(code, search_match, TokenExpressions)
    tokens = list(filter(lambda token: token.tokentype_ != TokenTypes.NONE, lexed))
    
    parsed, eof_token = parse(code, tokens)
    program = Program(loc_={'start': {'line': 1, 'index': 0}, "end":{"line":tokens[-1].loc_["start"]["line"], "index":tokens[-1].loc_["start"]["index"]}}, range_=[0, len(code)], body_=parsed)
    
    with open("output.json", "wb") as f:
        f.write(program.pretty_print().encode("utf-8"))
    
    time_start = time.time()
    result = interpret(code, program)
    time_stop = time.time()
    print("program finished in", round(time_stop-time_start, 5), "s")