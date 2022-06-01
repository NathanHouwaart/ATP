from ast import Return, operator
from ctypes.wintypes import PUSHORT
from inspect import stack
from pyclbr import Function
import sys
import os
import time
from itertools import islice
from cortexm0 import *

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Set, Tuple, Callable, Optional, Dict, List
from lexer_module.lexer import lex, search_match
from parser_module.parser import parse
from misc.token_types import *
from misc.node_types import *
from misc.error_message import generate_error_message
from misc.symbol_table import *
from arm_registers import *
from compiler_data_structures import *       
from cortexm0 import *

# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------  Helper Functions ------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

def get_attribute(method_name, default):
    if method_name in globals():
        return globals()[method_name]
    return default

def no_compile_method(code: str, node: Node, symbol_table: SymbolTable):
    print("no compile method for node type", type(node))
    return symbol_table

def calculate_num_nodes(code: str, node: Node, symbol_table: SymbolTable):
    if(type(node) == Identifier or type(node) == Literal):
        return 1
    elif(type(node) == BinaryExpression):
        left = 1 + calculate_num_nodes(code, node.left_, symbol_table)
        right = 1 + calculate_num_nodes(code, node.right_, symbol_table)
        if(right > left):
            return right
        else:
            return left
    return 1 + calculate_num_nodes(code, node, symbol_table)


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------  Compile Functions -----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


def add_function_arguments_to_symbol_table(symbol_table: SymbolTable, arguments: list[Literal], register_loc = 0):
    if len(arguments) == 0:
        return symbol_table
    
    head, *tail = arguments
    
    # Check if symbol is already defined. In that case, function has duplicate argument names
    if symbol_table_symbol_exists(symbol_table, head.name_):
        generate_error_message(head, code, "Duplicate function argument", True)
        
    # If not, add argument to symbol table
    symbol_table = symbol_table_set(symbol_table, head.name_ , VairableSymbol(head.name_, SymbolType.ARGUMENT, register_loc))
    return add_function_arguments_to_symbol_table(symbol_table, tail, register_loc + 1)



def compile_FunctionDeclaration(code: str, node: FunctionDeclaration, symbol_table: SymbolTable, call_stack):
    print("compile_FunctionDeclaration")
    
    # 1. Check if identifier is defined
    symbol_info = symbol_table_get(symbol_table, node.id_)                              # Get information from symbol table
    if symbol_info != None:                                                             # If already defined
        generate_error_message(node, node, code, "Redeclaration of function", True)     # Generate error message
    
    # 2. Check if function has no more than four parameters
    if(len(node.params_) > 4):
        generate_error_message(node, code, "Function has more than four parameters", True)
    
    # 3. Add function and parameters to parent symbol table
    symbol_table = symbol_table_set(symbol_table, node.id_, 
                                    FunctionSymbol(node.id_, SymbolType.FUNCTION, len(node.params_))) # Add callable name and number of params
    
    # 4. Create a new symbol table for the function, set parent symbol table accordingly
    function_symbol_table = SymbolTable(symbols={}, parent=symbol_table, return_symbols=[], return_stop=False, stack_variables=0)
    
    # 5. Recursively Add parameters to function symbol table
    function_symbol_table = add_function_arguments_to_symbol_table(function_symbol_table, node.params_)   # Add parameters to symbol table
    
    # 6. Reserve registers for arguments
    Registers.free_all_registers()
    Registers.allocate_register_range(0, len(node.params_))

    # 7. Write assebmly code for function
    cm0_create_label(node.id_)                                                                      # Create label for branch
    cm0_function_preamble(0)                                                                        # Write function preamble
    function_symbol_table = compile_loop(code, [node.body_], function_symbol_table, call_stack)     # Compile function body
    cm0_function_postamble(0)                                                                       # Write function postamble
    
    return symbol_table



def compile_ReturnStatement(code: str, node: ReturnStatement, symbol_table: SymbolTable, call_stack):
    print("compile_ReturnStatement")
    result, symbol_table = symbol_table_get_and_del_return_symbol(compile_loop(code, [node.argument_], symbol_table, call_stack + [ReturnStatement]))
    return symbol_table

# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------  Compile Other stf -----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

def compile_BlockStatement(code: str, node: BlockStatement, symbol_table: SymbolTable, call_stack):
    print("compile_BlockStatement")
    return compile_loop(code, node.body_, symbol_table, call_stack + [BlockStatement])


def compile_BinaryExpression(code: str, node: BinaryExpression, symbol_table: SymbolTable, call_stack):
    operator = node.operator_
    
    # Check which node to walk first: deepest node goes first in order to minimize stack usage    
    left = calculate_num_nodes(code, node.left_, symbol_table)
    right = calculate_num_nodes(code, node.right_, symbol_table)
    
    if(left > right):
        left , symbol_table = symbol_table_get_and_del_return_symbol(compile_loop(code, [node.left_], symbol_table, call_stack + [BinaryExpression]))
        right, symbol_table = symbol_table_get_and_del_return_symbol(compile_loop(code, [node.right_], symbol_table, call_stack + [BinaryExpression]))       
    else:
        right, symbol_table = symbol_table_get_and_del_return_symbol(compile_loop(code, [node.right_], symbol_table, call_stack + [BinaryExpression]))
        left , symbol_table = symbol_table_get_and_del_return_symbol(compile_loop(code, [node.left_], symbol_table, call_stack + [BinaryExpression]))
        print(right, left)

    if   operator == TokenTypes.PLUS          : symbol_table_add_return_symbol(symbol_table, cm0_add(left[0], right[0]))
    elif operator == TokenTypes.MINUS         : symbol_table_add_return_symbol(symbol_table, cm0_sub(left[0], right[0]))
    elif operator == TokenTypes.DIVIDE        : symbol_table_add_return_symbol(symbol_table, cm0_div(left[0], right[0], symbol_table))
    elif operator == TokenTypes.MULTIPLY      : symbol_table_add_return_symbol(symbol_table, cm0_mul(left[0], right[0]))
    # elif operator == TokenTypes.IS_EQUAL      : symbol_table_add_return_symbol()
    # elif operator == TokenTypes.GREATER_THAN  : symbol_table_add_return_symbol()
    # elif operator == TokenTypes.SMALLER_THAN  : symbol_table_add_return_symbol()
    # elif operator == TokenTypes.AND           : symbol_table_add_return_symbol()
    # elif operator == TokenTypes.OR            : symbol_table_add_return_symbol()
    
    return symbol_table

def present(arr, v): 
    return arr.count(v)


def compile_Identifier(code: str, node: Identifier, symbol_table: SymbolTable, call_stack):
    print("compile_Identifier")
    
    # 1. Check if identifier is defined
    symbol = symbol_table_get(symbol_table, node.name_)                            # Get information from symbol table
    if symbol == None:                                                             # If not defined
        generate_error_message(node, code, f"{node.name_} is not defined", True)        # Generate error message
    
    
    symbol_table_add_return_symbol(symbol_table, symbol.symbol_register)
    return symbol_table


def compile_VariableDeclaration(code: str, node: VariableDeclaration, symbol_table: SymbolTable, call_stack):
    print("compile_VariableDeclaration")
    # 1. Initialize variable
    symbol_table = compile_loop(code, [node.init_], symbol_table, call_stack + [VariableDeclaration])                       # Compile the initializer 
    return_symbol, symbol_table = symbol_table_get_and_del_return_symbol(symbol_table)  # Get the register that the initializer is stored in
    return_symbol = return_symbol[0]                                                    # Get the register number                   
    
    # 2. Check if variable is already defined
    symbol = symbol_table_get(symbol_table, node.id_)                                   # Get information from symbol table
    if symbol != None and type(symbol) != VairableSymbol:                               # If a symbol is found, check if it is a variable
        generate_error_message(node, code, f"Redefinition of {node.id_}", True)         # If not, generate error
    
    # 4a. if variable is already defined
    if symbol != None:                                                             # If a symbol is found, ask information about the symbol
        variable_stack_offset =  symbol_table_get_stack_variable_amt(symbol_table) * 4  # Get stack offset of variable
        cm0_store(return_symbol, variable_stack_offset)                                 # Overwrite the register that is already on the stack
    
    # 4b. if variable is not defined. define it
    else:
        symbol_table = symbol_table_set(symbol_table, node.id_, 
                                        VairableSymbol(node.id_, SymbolType.VARIABLE, return_symbol))     # Add new variable to symbol table with stack offset
    return symbol_table
 
 
 
def compile_Literal(code: str, node: Literal, symbol_table: SymbolTable, call_stack):
    symbol_table = symbol_table_add_return_symbol(symbol_table, cm0_movi(node.value_))
    return symbol_table



# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------- Compile Loop -------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

def compile_loop(code, program_nodes: List[Node], symbol_table: SymbolTable, call_stack : List[Node]) -> SymbolTable:
    if len(program_nodes) == 0 or symbol_table.return_stop == True:
        return symbol_table
    
    node, *tail = program_nodes   
    node_type = type(node)

    method_name  = f"compile_{type(node).__name__}"
    method       = get_attribute(method_name, no_compile_method)
    symbol_table = method(code, node, symbol_table, call_stack)
    
    return compile_loop(code, tail, symbol_table, call_stack)


def compile(code, program: Program):
    symbol_table = SymbolTable(symbols={}, parent=None, return_symbols=[], return_stop=False, stack_variables=0)
    symbol_table = symbol_table_set(symbol_table, "🖨", FunctionSymbol("__aeabi_idiv", SymbolType.FUNCTION, 1))
    # cm0_preamble()   
    compile_loop(code, program.body_, symbol_table, [])
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

    lexed = lex(code, search_match, TokenExpressions)
    tokens = list(filter(lambda token: token.tokentype_ != TokenTypes.NONE, lexed))

    parsed, eof_token = parse(code, tokens)
    program = Program(loc_={'start': {'line': 1, 'index': 0}, "end":{"line":tokens[-1].loc_["start"]["line"], "index":tokens[-1].loc_["start"]["index"]}}, range_=[0, len(code)], body_=parsed)
    
    with open("ast_to_interpret.json", "wb") as f:
        f.write(program.jsonify().encode("utf-8"))
    
    time_start = time.time()
    result = compile(code, program)
    time_stop = time.time()
    print("program finished in", round(time_stop-time_start, 5), "s")
    