from atexit import register
from posixpath import split
import sys
import os
import time

from httplib2 import FailedToDecompressContent

from cortexm0 import *
import io

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Set, Tuple, Callable, Optional, Dict, List
from lexer_module.lexer import lex, search_match
from parser_module.parser import parse
from misc.token_types import *
from misc.node_types import *
from misc.error_message import generate_error_message
from misc.symbol_table import *
from cortexm0 import *


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------  Helper Functions ------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

def get_attribute(
    method_name: str, 
    default: Callable
) -> Callable:
    """Search for a method name. Return default method if not found.

    Args:
        method_name: Name of the method to search for
        default: Default method to return if method is not found

    Return:
        Method to call or default method
    """
    if method_name in globals():
        return globals()[method_name]
    return default



def no_compile_method(
    code:           str, 
    node:           Node, 
    symbol_table:   SymbolTable, 
    call_stack:     List[Node]
):
    """Default method for nodes that are not implemented yet. Generates error message and
    exits the program.
    """
    print("no compile method for node type", type(node))
    exit()


def calculate_num_nodes(
    code: str, 
    node: Node, 
    symbol_table: SymbolTable
) -> int:
    """Function calculates the depth of a binary expression statement. This way,
    the register usage can be minimized, by calculating the deepest node first.
    
    Args:
        code        : String representation of the lexed, parsed, compiled code
        node        : Node that is being calculated
        symbol_table: Symbol table of the current scope
    
    Returns:
        Depth of the current node. Returns 0 if node is not a binary expression
    """
    if(type(node) == BinaryExpression):
        left = 1 + calculate_num_nodes(code, node.left_, symbol_table)
        right = 1 + calculate_num_nodes(code, node.right_, symbol_table)
        if(right > left):
            return right
        else:
            return left
    else:
        return 1



def check_present(
    arr:    List[Node], 
    what:   Node
) -> int:
    """Helper function checks if and how many a certain element is present in a list.

    Args:
        arr: List to check
        what: Element to check for

    Returns:
        Number of occurences of the element in the list
    """
    if(len(arr) == 0):
        return 0
    
    head, *tail = arr
    if(type(head) == what):
        return 1 + check_present(tail, what)
    return check_present(tail, what)



def node_range_to_label(
    node: Node
) -> str:
    """Function to convert a node range to a string label which can be used to create unique pseudo register names for the same variables"""
    return str(node.range_[0]) + "_" + str(node.range_[1])


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------  Compile Functions -----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

def pseudo_compile_CallExpression(
    code:           str, 
    node:           CallExpression, 
    symbol_table:   SymbolTable, 
    call_stack:     List[Node],
    pseudo_code:    str
) -> Tuple[SymbolTable, str]:
    """Pseudo compile a call expression in to intermediate assembly code. 

    Note: 
        This function generates pseudo code for a call expression. The assembly created will contain non existant assembly keywords and 
        will contain pseudo register names. Both of these will later be replaced with actual assembly code.
    
    Args:
        code         : String representation of the lexed, parsed, compiled code
        node         : Node that is being pseudo compiled
        symbol_table : Symbol table of the current scope
        call_stack   : Call stack of nodes that are currently being compiled
    
    Returns:
        A Tuple containing:
            1. Symbol table of the current scope 
            2. Pseudo assembly code of the program
    """
    # print("compile_CallExpression")
    symbol_table, pseudo_code = pseudo_compile_loop(code, node.arguments_, symbol_table, call_stack + [node], pseudo_code)
    return_value, symbol_table = symbol_table_get_and_del_return_symbol(symbol_table)

    # Prepare for function call by preserving registers that are being potentially overwritten

    pseudo_code += "\tnotpush".ljust(10) + "{ "
    for return_symbol in return_value:
        pseudo_code += return_symbol.symbol_register + " "
    pseudo_code += "}\n"

    # Move registers correct argument index
    for i in range(len(return_value)):
        pseudo_code = cm0_mov(pseudo_code, f"r{i}", return_value[i].symbol_register)

    # Call function
    pseudo_code = cm0_call(pseudo_code, node.callee_.name_)

    # Move registers back to correct registers
    for i in range(len(return_value)):
        pseudo_code = cm0_mov(pseudo_code, return_value[i].symbol_register, f"r{i}")

    # Restore registers that were potentially overwritten
    pseudo_code += "\tnotpop".ljust(10) + "{ "
    for return_symbol in return_value:
        pseudo_code += return_symbol.symbol_register + " "
    pseudo_code += "}\n"

    # Make a pseudo symbol for a variable that is being returned
    if(type(call_stack[-1]) == VariableDeclaration):
        pseudo_code = cm0_mov(pseudo_code, call_stack[-1].id_ + "_reg", return_value[0].symbol_register)

    symbol_table = symbol_table_add_return_symbol(symbol_table, return_value[0])
    return symbol_table, pseudo_code



def add_function_arguments_to_symbol_table(
    symbol_table: SymbolTable, 
    arguments: List[Literal], 
    register_loc = 0
) -> SymbolTable:
    """
    Function recursively adds function arguments to the symbol table.
    
    Args:
        symbol_table: Symbol table of the current scope
        arguments   : List of arguments of the function
        register_loc: Register location of the current argument, defaults to 0 (r0)

    returns:
        Symbol table of the current scope with the arguments added
    """
    if len(arguments) == 0:
        return symbol_table
    
    head, *tail = arguments
    
    # Check if symbol is already defined. In that case, function has duplicate argument names
    if symbol_table_symbol_exists(symbol_table, head.name_):
        generate_error_message(head, code, "Duplicate function argument", True)
        
    # If not, add argument to symbol table
    symbol_table = symbol_table_set(symbol_table, head.name_ , VairableSymbol(head.name_, SymbolType.ARGUMENT, "r{}".format(register_loc)))
    return add_function_arguments_to_symbol_table(symbol_table, tail, register_loc + 1)



def pseudo_compile_FunctionDeclaration(
    code: str, 
    node: FunctionDeclaration, 
    symbol_table: SymbolTable, 
    call_stack: List[Node],
    pseudo_code:    str
) -> Tuple[SymbolTable, str]:
    """Pseudo compile a function in to intermediate assembly code.

    Also adds a .global directive to the assembly code.

    Args:
        code         : String representation of the lexed, parsed, compiled code
        node         : Node that is being pseudo compiled
        symbol_table : Symbol table of the current scope
        call_stack   : Call stack of nodes that are currently being compiled

    Returns:
        A Tuple containing:
            1. Symbol table of the current scope
            2. Pseudo assembly code of the program
    """
    
    # 1. Check if identifier is already defined
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
    # Registers.allocate_register_range(0, len(node.params_))

    # 7. Write assebmly code for function
    pseudo_code = cm0_global(pseudo_code, node.id_)
    pseudo_code = cm0_label(pseudo_code, node.id_)                                                                                          # Create label for branch
    pseudo_code = cm0_function_preamble(pseudo_code, 0)                                                                                     # Write function preamble
    function_symbol_table, pseudo_code = pseudo_compile_loop(code, [node.body_], function_symbol_table, call_stack + [node], pseudo_code)   # Compile function body
    pseudo_code = cm0_function_postamble(pseudo_code, node.id_, 0)                                                                          #  Write function postamble
    
    return symbol_table, pseudo_code



def pseudo_compile_ReturnStatement(
    code:           str, 
    node:           ReturnStatement, 
    symbol_table:   SymbolTable, 
    call_stack :    List[Node],
    pseudo_code:    str
) -> Tuple[SymbolTable, str]:
    """Pseudo compile a return statement in to intermediate assembly code.

    Args:
        code         : String representation of the lexed, parsed, compiled code
        node         : Node that is being pseudo compiled
        symbol_table : Symbol table of the current scope
        call_stack   : Call stack of nodes that are currently being compiled
        pseudo_code  : Pseudo assembly code of the program
    
    Returns:
        A Tuple containing:
            1. Symbol table of the current scope
            2. Pseudo assembly code of the program
    """
    # print("compile_ReturnStatement")
    symbol_table, pseudo_code = pseudo_compile_loop(code, [node.argument_], symbol_table, call_stack + [node], pseudo_code)
    result, symbol_table = symbol_table_get_and_del_return_symbol(symbol_table)
    
    pseudo_code = cm0_mov(pseudo_code, "r0", result[0].symbol_register)
    if(type(call_stack[0]) == FunctionDeclaration and check_present(call_stack, IfStatement)):
        pseudo_code = cm0_b(pseudo_code, call_stack[0].id_ + "_end")
    return symbol_table, pseudo_code



def pseudo_compile_BlockStatement(
    code: str, 
    node: BlockStatement, 
    symbol_table: SymbolTable, 
    call_stack: List[Node],
    pseudo_code:    str
) -> Tuple[SymbolTable, str]:
    """Function pseudo compiles a block statement in to intermediate assembly code.

    Args:
        code         : String representation of the lexed, parsed, compiled code
        node         : Node that is being pseudo compiled
        symbol_table : Symbol table of the current scope
        call_stack   : Call stack of nodes that are currently being compiled
        pseudo_code  : Pseudo assembly code of the program

    Returns:
        A Tuple containing:
            1. Symbol table of the current scope
            2. Pseudo assembly code of the program
    """
    return pseudo_compile_loop(code, node.body_, symbol_table, call_stack + [node], pseudo_code)



def pseudo_compile_BinaryExpression(
    code: str, 
    node: BinaryExpression, 
    symbol_table: SymbolTable, 
    call_stack: Node,
    pseudo_code:    str
) -> Tuple[SymbolTable, str]:
    """
    Pseudo compile a binary expression in to intermediate assembly code.
    
    Args:
        code         : String representation of the lexed, parsed, compiled code
        node         : Node that is being pseudo compiled
        symbol_table : Symbol table of the current scope
        call_stack   : Call stack of nodes that are currently being compiled
        pseudo_code  : Pseudo assembly code of the program

    Returns:
        A Tuple containing:
            1. Symbol table of the current scope
            2. Pseudo assembly code of the program
    """
    operator = node.operator_

    # Check which node to walk first: deepest node goes first in order to minimize register usage    
    left  = calculate_num_nodes(code, node.left_, symbol_table)
    right = calculate_num_nodes(code, node.right_, symbol_table)
    
    # Compile left and right nodes
    if(left > right):
        # Left
        symbol_table, pseudo_code = pseudo_compile_loop(code, [node.left_], symbol_table, call_stack + [node], pseudo_code)
        left , symbol_table = symbol_table_get_and_del_return_symbol(symbol_table)

        # Right
        symbol_table, pseudo_code = pseudo_compile_loop(code, [node.right_], symbol_table, call_stack + [node], pseudo_code)
        right, symbol_table = symbol_table_get_and_del_return_symbol(symbol_table)       
    else:
        # Right
        symbol_table, pseudo_code = pseudo_compile_loop(code, [node.right_], symbol_table, call_stack + [node], pseudo_code)
        right, symbol_table = symbol_table_get_and_del_return_symbol(symbol_table)

        # Left
        symbol_table, pseudo_code = pseudo_compile_loop(code, [node.left_], symbol_table, call_stack + [node], pseudo_code)
        left , symbol_table = symbol_table_get_and_del_return_symbol(symbol_table)

    right = right[0]
    left  = left[0]

    # Check which pseudo register to use
    if(type(call_stack[-1]) == VariableDeclaration):
        result_reg_name = call_stack[-1].id_ + "_reg"
    elif(type(call_stack[-1]) == ReturnStatement):
        result_reg_name = "function_return" + "_reg"
    else:
        result_reg_name = right.symbol_name + "_" + left.symbol_name + "_res" + "_reg"
    
    # Check which operator to use
    if operator == TokenTypes.PLUS:
        pseudo_code  = cm0_add(pseudo_code, result_reg_name,  right.symbol_register, left.symbol_register)
        symbol_table = symbol_table_add_return_symbol(symbol_table, VairableSymbol(result_reg_name, SymbolType.VARIABLE, result_reg_name))

    elif operator == TokenTypes.MINUS: 
        pseudo_code  = cm0_sub(pseudo_code, result_reg_name,  left.symbol_register, right.symbol_register)
        symbol_table = symbol_table_add_return_symbol(symbol_table, VairableSymbol(result_reg_name, SymbolType.VARIABLE, result_reg_name))

    elif operator == TokenTypes.MULTIPLY: 
        pseudo_code  = cm0_mul(pseudo_code, result_reg_name, right.symbol_register, left.symbol_register)
        symbol_table = symbol_table_add_return_symbol(symbol_table, VairableSymbol(result_reg_name, SymbolType.VARIABLE, result_reg_name))

    elif operator == TokenTypes.IS_EQUAL:
        branch_label_name = right.symbol_name + "_eq_" + left.symbol_name + "_res_equal"
        pseudo_code = cm0_movi(pseudo_code, result_reg_name, 1)
        pseudo_code = cm0_cmp(pseudo_code, right.symbol_register, left.symbol_register)
        pseudo_code = cm0_beq(pseudo_code, branch_label_name)
        pseudo_code = cm0_movi(pseudo_code, result_reg_name, 0)
        pseudo_code = cm0_label(pseudo_code, branch_label_name)
        symbol_table = symbol_table_add_return_symbol(symbol_table, VairableSymbol(result_reg_name, SymbolType.VARIABLE, result_reg_name))

    elif operator == TokenTypes.GREATER_THAN  : 
        branch_label_name = right.symbol_name + "_gt_" + left.symbol_name + "_res_greater_than"
        pseudo_code = cm0_movi(pseudo_code, result_reg_name, 1)
        pseudo_code = cm0_cmp(pseudo_code, left.symbol_register, right.symbol_register)
        pseudo_code = cm0_bgt(pseudo_code, branch_label_name)
        pseudo_code = cm0_movi(pseudo_code, result_reg_name, 0)
        pseudo_code = cm0_label(pseudo_code, branch_label_name)
        symbol_table = symbol_table_add_return_symbol(symbol_table, VairableSymbol(result_reg_name, SymbolType.VARIABLE, result_reg_name))

    elif operator == TokenTypes.SMALLER_THAN  : 
        branch_label_name = right.symbol_name + "_lt_" + left.symbol_name + "_res_less_than"
        pseudo_code = cm0_movi(pseudo_code, result_reg_name, 1)
        pseudo_code = cm0_cmp(pseudo_code, left.symbol_register, right.symbol_register)
        pseudo_code = cm0_blt(pseudo_code, branch_label_name)
        pseudo_code = cm0_movi(pseudo_code, result_reg_name, 0)
        pseudo_code = cm0_label(pseudo_code, branch_label_name)
        symbol_table = symbol_table_add_return_symbol(symbol_table, VairableSymbol(result_reg_name, SymbolType.VARIABLE, result_reg_name))

    elif operator == TokenTypes.AND:
        pseudo_code = cm0_and(pseudo_code, result_reg_name,  right.symbol_register, left.symbol_register)
        symbol_table = symbol_table_add_return_symbol(symbol_table, VairableSymbol(result_reg_name, SymbolType.VARIABLE, result_reg_name))

    elif operator == TokenTypes.OR: 
        pseudo_code = cm0_or(pseudo_code, result_reg_name,  right.symbol_register, left.symbol_register)
        symbol_table = symbol_table_add_return_symbol(symbol_table, VairableSymbol(result_reg_name, SymbolType.VARIABLE, result_reg_name))
    return symbol_table, pseudo_code



def pseudo_compile_IfStatement(
    code: str, 
    node: Identifier, 
    symbol_table: SymbolTable, 
    call_stack: List[Node],
    pseudo_code:    str
) -> Tuple[SymbolTable, str]:
    """Function to pseudo compile an if statement

    Args:
        code: The code to pseudo compile
        node: The node to pseudo compile
        symbol_table: The symbol table to use
        call_stack: The call stack to use
        pseudo_code: The pseudo code to use

    Returns:
        A Tuple containing:
            1. Symbol table of the current scope
            2. Pseudo assembly code of the program
    """
    # print("compile_IfStatement")
    if_end_label = call_stack[0].id_ + "_if_end_" + str(check_present(call_stack, IfStatement)) + "_" + node_range_to_label(node)

    symbol_table, pseudo_code = pseudo_compile_loop(code, [node.test_], symbol_table, call_stack + [node], pseudo_code)
    test_result, symbol_table = symbol_table_get_and_del_return_symbol(symbol_table)
    
    pseudo_code = cm0_cmp(pseudo_code, test_result[0].symbol_register, "#0")

    if type(call_stack[0]) == FunctionDeclaration:
        branch_label = call_stack[0].id_ + "_if_false_" + str(check_present(call_stack, IfStatement)) + "_" + node_range_to_label(node)
        if node.alternate_:
            pseudo_code = cm0_beq(pseudo_code, branch_label)
        else:
            pseudo_code = cm0_beq(pseudo_code, if_end_label)    
    else:
        raise Exception("Code outside of function not supported")

    symbol_table, pseudo_code =  pseudo_compile_loop(code, [node.consequent_], symbol_table, call_stack + [node], pseudo_code)
    test_result, symbol_table = symbol_table_get_and_del_return_symbol(symbol_table)
    if(node.alternate_):
        pseudo_code = cm0_b(pseudo_code, if_end_label)
        pseudo_code = cm0_label(pseudo_code, branch_label)
        symbol_table, pseudo_code = pseudo_compile_loop(code, [node.alternate_], symbol_table, call_stack + [node], pseudo_code)
        test_result, symbol_table = symbol_table_get_and_del_return_symbol(symbol_table)
        pseudo_code = cm0_label(pseudo_code, if_end_label)
    else:
        pseudo_code = cm0_label(pseudo_code, if_end_label)
    return symbol_table, pseudo_code



def pseudo_compile_Identifier(
    code: str, 
    node: Identifier, 
    symbol_table: SymbolTable, 
    call_stack: List[Node],
    pseudo_code:    str
) -> Tuple[SymbolTable, str]:
    """Function pseudo compiles an identifier
    
    Args:
        code: The code to pseudo compile
        node: The node to pseudo compile
        symbol_table: The symbol table to use
        call_stack: The call stack to use
        pseudo_code: The pseudo code to use

    Returns:
        A Tuple containing:
            1. Symbol table of the current scope
            2. Pseudo assembly code of the program
    """    
    # 1. Check if identifier is defined
    symbol = symbol_table_get(symbol_table, node.name_)                            # Get information from symbol table
    if symbol == None:                                                             # If not defined
        generate_error_message(node, code, f"{node.name_} is not defined", True)    # Generate error message
    
    # 2. Add the found symbol to symbol table return list
    symbol_table_add_return_symbol(symbol_table, symbol)
    return (symbol_table, pseudo_code)



def pseudo_compile_VariableDeclaration(
    code: str, 
    node: VariableDeclaration, 
    symbol_table: SymbolTable, 
    call_stack: List[Node],
    pseudo_code:    str
) -> Tuple[SymbolTable, str]:
    """Function pseudo compiles a variable declaration

    Args:
        code: The code to pseudo compile
        node: The node to pseudo compile
        symbol_table: The symbol table to use
        call_stack: The call stack to use
        pseudo_code: The pseudo code to use

    Returns:
        A Tuple containing:
            1. Symbol table of the current scope
            2. Pseudo assembly code of the program
    """
    # print("compile_VariableDeclaration")
    
    # 1. Check if symbol is already defined as something other than a variable
    symbol = symbol_table_get(symbol_table, node.id_)                           
    if symbol != None and type(symbol) != VairableSymbol:                       
        generate_error_message(node, code, f"Redefinition of {node.id_}", True) 

    # 2. Initialize variable
    symbol_table, pseudo_code = pseudo_compile_loop(code, [node.init_], symbol_table, call_stack + [node], pseudo_code)      # Compile the initializer 
    return_symbol, symbol_table = symbol_table_get_and_del_return_symbol(symbol_table)                          # Get the register that the initializer is stored in
    return_symbol = return_symbol[0]                                                                            # Get the register number               
    
    # 3. Add variable to symbol table
    symbol_table = symbol_table_set(symbol_table, node.id_, 
                                    VairableSymbol(node.id_, SymbolType.VARIABLE, node.id_ + "_reg"))           # Add new variable to symbol table with stack offset

    return symbol_table, pseudo_code
 
 
 
def pseudo_compile_Literal(
    code: str, 
    node: Literal, 
    symbol_table: SymbolTable, 
    call_stack: List[Node],
    pseudo_code:    str
) -> Tuple[SymbolTable, str]:
    """Function pseudo compiles a literal
    
    Args:
        code: The code to pseudo compile
        node: The node to pseudo compile
        symbol_table: The symbol table to use
        call_stack: The call stack to use
        pseudo_code: The pseudo code to use

    Returns:
        A Tuple containing:
            1. Symbol table of the current scope
            2. Pseudo assembly code of the program
    """

    # 1. Choose correct pseudo register name based on call stack
    if(type(call_stack[-1]) == VariableDeclaration):
        literal_id = call_stack[-1].id_
    else:
        literal_id = "literal_value_" + node.raw_ + "_" + node_range_to_label(node)

    # 2. Move literal value to pseudo register
    pseudo_code = cm0_movi(pseudo_code, literal_id + "_reg", node.value_)

    # 3. Add literal to symbol table
    symbol = LiteralSymbol(literal_id, SymbolType.LITERAL, literal_id + "_reg")
    symbol_table = symbol_table_set(symbol_table, literal_id, symbol)
    symbol_table = symbol_table_add_return_symbol(symbol_table, symbol)

    return symbol_table, pseudo_code



# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------- Pseudo Loop -------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

def pseudo_compile_loop(
    code:           str, 
    program_nodes:  List[Node], 
    symbol_table:   SymbolTable, 
    call_stack :    List[Node], #= [], 
    pseudo_code:    str # = ""
) -> Tuple[SymbolTable, str]:
    """Function recursively loops over all the program nodes to compile them.

    Checks the current node type, and calls the appropriate function to compile the node using the get_attribute helper function.
    Throws an error if the compile loop is called on a node that is not supported.

    Compile Loop returns when the program_nodes list is empty.

    Args:
        code:           The code that is being lexed, parsed, and compiled.
        program_nodes:  A list of nodes that are to be compiled.
        symbol_table:   The symbol table of the current scope.
        call_stack:     A list of nodes that are currently being compiled.
        pseudo_code:    The pseudo code that is being compiled.

    Returns:
        A Tuple containing:
            1. Symbol table of the current scope
            2. Pseudo assembly code of the program
    """
    if len(program_nodes) == 0 or symbol_table.return_stop == True:
        return symbol_table, pseudo_code
    
    node, *tail = program_nodes   
    node_type = type(node)

    method_name  = f"pseudo_compile_{type(node).__name__}"
    method       = get_attribute(method_name, no_compile_method)
    symbol_table, pseudo_code = method(code, node, symbol_table, call_stack, pseudo_code)
    
    return pseudo_compile_loop(code, tail, symbol_table, call_stack, pseudo_code)

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------- Compile Pseudo Code --------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


def regnames_count_predicate(
    register_name:str,
    register_count: Dict[str, int]
) -> Dict[str, int]:
    """
    Function to increase or add a new pseudo register to the register_count dictionary.

    Args:
        register_name: The name of the register to increase or add.
        register_count: The dictionary containing the number of times each register is used.
    
    Returns:
        The updated register_count dictionary.
    """
    if register_name in register_count:
        register_count[register_name][0] +=1
    else:
        register_count[register_name] = [1, None]
    return register_count



def regnames_count_recursive(
    formatted_code: List[Any],
    register_count: Dict[str, int] = {}
) -> Dict[str, int]:
    """
    Function recursively traverses the formatted_code list and increase or adds a new pseudo register to the register_count dictionary.
    
    Args:
        formatted_code: Lines of pseudo code that are to be counted
        register_count: The dictionary containing the number of times each register is used.

    Returns:
        The updated register_count dictionary.
    """
    if len(formatted_code) == 0:
        return register_count
    
    head, *tail = formatted_code
    filtered        = list(filter(lambda x: x[0] != "#" and x !="sp", head[1:]))
    register_count  = list(map(lambda x, y=register_count: regnames_count_predicate(x, y), filtered))[0]

    return regnames_count_recursive(tail, register_count)



def format_pseudo_output(
    line: str
) -> List[List[str]]:
    """Function formats the pseudo code output in a two dimentional list of lines whith keywords and registers
    
    Args:
        psuedo_code: The pseudo code to format

    Returns:
        A two dimentional list of lines with keywords and registers
    """
    
    if(line == "" or ":" in line or re.findall(r"\blr\b", line) or re.findall(r"\bpc\b", line)):
        return None
    line = line.replace(',', ' ').split()
    if line[0] ==  "beq" or line[0] ==  "b"  or line[0] == "bne" or line[0] == line or line[0] == "bgt" or line[0] == "blt" or line[0] == "str" or line[0] == "ldr" or line[0] == "bl" or line[0] == ".global":
        return None
    return line



def pseudo_compile(
    code: str, 
    program: Program
) -> str:
    """
    Pseudo compile the program into CM0 code.

    The steps taken are:
        1. Create a new symbol table for the program
        2. Loop over every node in the program
        3. Compile every node into pseudo code

    Args:
        code:    The code to compile
        program: The AST of the program to compile
    
    Returns:
        The pseudo code of the program
    """

    # 1. Create a symbol table for the program
    symbol_table = SymbolTable(symbols={}, parent=None, return_symbols=[], return_stop=False, stack_variables=0)
    
    # 2. Pseudo compile the program
    symbol_table, pseudo_code = pseudo_compile_loop(code, program.body_, symbol_table, [], "")
    return pseudo_code



def allocate_function_registers(
    register : str,
    register_count: Dict[str, int]
)-> Dict[str, int]:
    """
    Function allocates function registers and saves them in the register_count dictionary.

    Args:
        register: The register to allocate
        register_count: The dictionary containing the number of times each register is used.

    Returns:
        The updated register_count dictionary.
    """
    if register in register_count:
        Registers.register_status[register] = RegisterStatus.ALLOCATED
        register_count[register][1] = register
    return register_count


def replace_pseudo_register_with_real_register(
    code_line : str, 
    word_to_replace : str,
    register_count : Dict[str, int],
    register_list: List[str]
) -> Optional[Tuple[str, Dict[str, int]]]:
    """
    Function tries to replace the 'word_to_replace' with an actual register.
    It does so by recursively looping over the registers that are present in the register_count 
    dictionary.

    Args:
        code_line:          The line of code which contains the pseudo register to be replaced
        word_to_replace:    The pseudo register to be replaced
        register_count:     The dictionary containing the number of times each register is used
        register_list:      Tries to find these registers in the code_line

    Returns:
        Either None or a tuple containing:
            1. The line of code with the pseudo register replaced with a real register
            2. The dictionary containing the number of times each pseudo register is still used

        None is returned if the lined contained no registers that could be replaced
    """
    if len(register_list) == 0:
        return None

    register, *tail =register_list

    regex = re.compile(r"\b" + register + r"\b")
    if regex.match(word_to_replace):
        if(register_count[register][1] == None):
            allocated_reg = Registers.allocate_register()
            register_count[register][1] = allocated_reg
            code_line = re.sub(regex, " " + allocated_reg + " ", code_line)
        else:
            code_line = re.sub(regex, " " + register_count[register][1] + " ", code_line)
        register_count[register][0] -= 1
        if(register_count[register][0] == 0):
            Registers.free_register(register_count[register][1])
            register_count[register][1] = None
        if(register_count[register][0] < 0):
            print("ERROR: register count < 0")
            exit(1)
        return code_line, register_count
    return replace_pseudo_register_with_real_register(code_line, word_to_replace, register_count, tail)
    

def assign_registers_to_line(
    pseudo_code_line : str,
    reversed_split_line : List[str],
    register_count : Dict[str, int],
    compiled_line : str = ""
) -> Tuple[str, Dict[str, int]]:
    """
    Function and subfunctions replace pseudo registers in a code line with real registers. 
    
    Args:
        pseudo_code_line: The line of code to replace pseudo registers with real registers
        reversed_split_line: The line of code split into words
        register_count: The dictionary containing the number of times each register is used
        compiled_line: The line of code with pseudo registers replaced with real registers

    Returns:
        A tuple containing:
            1. The line of code with pseudo registers replaced with real registers
            2. The dictionary containing the number of times each pseudo register is still used
    """
    if len(reversed_split_line) == 0:
        # A
        compiled_line += pseudo_code_line + "\n"
        return compiled_line, register_count

    head, *tail = reversed_split_line
    result = replace_pseudo_register_with_real_register(pseudo_code_line, head, register_count, register_count)
    if not result:
        # skip line if no registers were replaced
        return assign_registers_to_line(pseudo_code_line, tail, register_count, compiled_line)

    pseudo_code_line, register_count = result
    return assign_registers_to_line(pseudo_code_line, tail, register_count, compiled_line)


def compile_pseudo_code_line(
    pseudo_code_line : str,
    split_line : List[str],
    compiled_code : str,
    register_count : Dict[str, int]
) -> Tuple[str, Dict[str, int]]:
    """
    Function and subrunctions recursively loop over pesudo code lines to replace the pseudo registers with real registers.

    Args:
        pseudo_code_line:   The line of code to replace pseudo registers with real registers
        split_line:         The line of code split into words
        compiled_code:      Compiled code
        register_count:     The dictionary containing the number of times each pseudo register is still used

    Returns:
        A tuple containing:
            1. The compiled code thus far
            2. The dictionary containing the number of times each pseudo register is still used
    """

    # Replace pseudo registers with real registers
    compiled_line, register_count = assign_registers_to_line(pseudo_code_line, list(reversed(split_line)), register_count)

    # Optionally Replace notpush and notpop with real registers. 
    # Add compiled lines to compiled code
    regex_not_push = re.compile(r"\b" + "notpush" + r"\b")
    regex_not_pop = re.compile(r"\b" + "notpop" + r"\b")
    if regex_not_push.findall(compiled_line):
        potential_push_registers = ["r0", "r1", "r2", "r3"]
        regex = re.compile(r"\b" + "r[0-9]" + r"\b")

        registers_to_push = list(filter(lambda x, not_push_registers=re.findall(regex, compiled_line): False if x in not_push_registers else True, potential_push_registers))
        compiled_code += "\tpush".ljust(10) + "{ " + " , ".join(registers_to_push) + " }\n"
   
    elif regex_not_pop.findall(compiled_line):
        potential_pop_registers = ["r0", "r1", "r2", "r3"]
        regex = re.compile(r"\b" + "r[0-9]" + r"\b")

        registers_to_push = list(filter(lambda x, not_push_registers=re.findall(regex, compiled_line): False if x in not_push_registers else True, potential_pop_registers))
        compiled_code += "\tpop".ljust(10) + "{ " + " , ".join(registers_to_push) + " }\n"
    else:
        compiled_code += compiled_line
    
    return compiled_code, register_count



def compile_pseudo_code_loop(
    unformatted_pseudo_code: str, 
    register_count : Dict[str, int],
    compiled_code :str = "",
) -> str:
    """
    Function and subfunctions recursively loop over pesudo code lines and compile them into real coretx-m0 code.

    Args:
        unformatted_pseudo_code     : The unformatted pseudo code
        register_count              : The dictionary containing the number of times each pseudo register is still used
        compiled_code               : String containing the compiled code

    Returns:
        string containing the compiled code
    """
    if len(unformatted_pseudo_code) == 0:
        return compiled_code

    pseudo_compiled_line, *tail = unformatted_pseudo_code
    pseudo_compiled_split_line = pseudo_compiled_line.split()
    pseudo_compiled_split_line = list(filter(lambda x: x != ",", pseudo_compiled_split_line))
    
    # Skip empty lines
    if not pseudo_compiled_split_line:
        compiled_code += "\n"

    # Skip branch, load, store, push and pop lines
    elif  pseudo_compiled_split_line[0] == "beq" or pseudo_compiled_split_line[0] == "bne" or pseudo_compiled_split_line[0] == "bgt" or pseudo_compiled_split_line[0] == "blt" or pseudo_compiled_split_line[0] == "b" or \
          pseudo_compiled_split_line[0] == "str" or pseudo_compiled_split_line[0] == "ldr" or pseudo_compiled_split_line[0] == "bl" or pseudo_compiled_split_line[0][0] == "." or pseudo_compiled_split_line[0][-1] == ":" or \
          pseudo_compiled_split_line[0] == "push" or pseudo_compiled_split_line[0] == "pop":
        compiled_code += pseudo_compiled_line + "\n"
    else:

    # For everything else, replace pseudo registers with real registers
        compiled_code, register_count = compile_pseudo_code_line(pseudo_compiled_line, pseudo_compiled_split_line, compiled_code, register_count)
    
    # Loop until all lines are compiled
    return compile_pseudo_code_loop(tail, register_count, compiled_code)


def compile_pseudo_code(
    code: str, 
    pseudo_code: str
) -> str:
    """
    Compile the generated pseudo code into actual Cortex-m0 assembly code.

    Steps taken to compile:
        1. Split the pseudo code into lines
        2. Remove empty lines
        3. Count the number of times each pseudo register is used and store it in register_count
        4. Replace pseudo registers with real registers. Do this from right to left, so that the rightmost register is replaced first.
        5. For each pseudo register it encounters do:
            5a. Allocate a cortex m0 registers for the pseudo register and store the allocated register it in register_count
            5b. Subtract 1 from the number of times the pseudo register is still used
            5c. If the number of times the pseudo register is still used is 0, free the cortex m0 register
        6. Replace notpush and notpop with real registers. (invert them)
    
    Args:
        code:           The code that is being lexed, parsed, and compiled.
        pseudo_code:    The pseudo code to compile

    Returns:
        The compiled code
    """
    formatted_pseudo_output = list(map(format_pseudo_output, pseudo_code.split("\n")))
    formatted_pseudo_output = list(filter(lambda x: x != None, formatted_pseudo_output))

    register_count          = regnames_count_recursive(formatted_pseudo_output)

    # Set function parameters to allcoated state
    Registers.free_all_registers()

    register_count          = list(map(lambda x, y=register_count: allocate_function_registers(x, y), Registers.register_status))[0]
    compiled_code           = compile_pseudo_code_loop(pseudo_code.split("\n"), register_count)
    return compiled_code
    



def compile(
    code: str, 
    program: Program
) -> str:
    """Function compiles the program into CM0 code.

    Returns a string containing the compiled code, which can be written
    to an output file.

    args:
        code:  Code that is being lexed, parsed, and compiled.
        program: The AST of the program to compile
    
    returns:
        A string containing the compiled code.
    """
    pseudo_compiled_code    = pseudo_compile(code, program)
    compiled_code           = compile_pseudo_code(code, pseudo_compiled_code)
    
    preamble = ".cpu cortex-m0\n.text\n.align 4\n\n"
    return preamble + compiled_code
    
    


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Expected filename")
        exit()
  
    with open(sys.argv[1], "rb") as f:
        code = f.read().decode("utf-8")  

    lexed = lex(code, search_match, TokenExpressions)
    tokens = list(filter(lambda token: token.tokentype_ != TokenTypes.NONE, lexed))

    parsed, eof_token = parse(code, tokens)
    program = Program(loc_={'start': {'line': 1, 'index': 0}, "end":{"line":tokens[-1].loc_["start"]["line"], "index":tokens[-1].loc_["start"]["index"]}}, range_=[0, len(code)], body_=parsed)
    
    with open("ast_to_interpret.json", "wb") as f:
        f.write(program.jsonify().encode("utf-8"))
    
    time_start = time.time()
    result = compile(code, program)
    print(result)
    time_stop = time.time()
    print("program finished in", round(time_stop-time_start, 5), "s")
    