import sys
import os
import time

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
        pseudo_code  = cm0_mul(result_reg_name, right.symbol_register, left.symbol_register)
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
# ------------------------------------------------- Compile Loop -------------------------------------------------------
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



def regnames_count(
    code: str, 
    register_count: Dict[str, int] = {}
) -> Dict[str, int]:
    """Function counds the number of times a specific pseudo register is used in the code. It
    stores the results in a dictionary."""
    for line in code:
        for i in range(1, len(line)):
            if line[i][0] == "#":
                continue
            if line[i] == "sp":
                continue
            if line[i] in register_count:
                register_count[line[i]][0] += 1
            else:
                register_count[line[i]] = [1, None]
    return register_count


def format_pseudo_output(
    psuedo_code: str
) -> List[List[str]]:
    """Function formats the pseudo code output in a two dimentional list of lines whith keywords and registers
    
    Args:
        psuedo_code: The pseudo code to format

    Returns:
        A two dimentional list of lines with keywords and registers
    """
    formatted_psuedo_code = []
    for line in psuedo_code.split("\n"):
        if(line == "" or ":" in line or re.findall(r"\blr\b", line) or re.findall(r"\bpc\b", line)):
            continue
        line = line.replace(',', ' ').split()
        if line[0] ==  "beq" or line[0] ==  "b"  or line[0] == "bne" or line[0] == line or line[0] == "bgt" or line[0] == "blt" or line[0] == "str" or line[0] == "ldr" or line[0] == "bl" or line[0] == ".global":
            continue
        formatted_psuedo_code.append(line)
    return formatted_psuedo_code



def pseudo_compile(code: str, program: Program):
    """
    Pseudo compile the program into CM0 code.

    The steps taken are:
        1. Create a new symbol table for the program
        2. Loop over every node in the program
        3. Compile the node into pseudo code

    args:
        code:    The code to compile
        program: The AST of the program to compile
    """

    # 1. Create a symbol table for the program
    symbol_table = SymbolTable(symbols={}, parent=None, return_symbols=[], return_stop=False, stack_variables=0)
    
    # 2. Pseudo compile the program
    symbol_table, pseudo_code = pseudo_compile_loop(code, program.body_, symbol_table, [], "")
    
    formatted_pseudo_output = format_pseudo_output(pseudo_code)
    # for line in formatted_pseudo_output:
    #     print(line)

    register_count = {}
    register_count = regnames_count(formatted_pseudo_output, register_count)
    print()
    for register in register_count:
        print(f"{register}".ljust(60), f"{register_count[register]}")
    print()

    # Set function parameters to allcoated state
    Registers.free_all_registers()
    for register in Registers.register_status:
        if register in register_count:
            Registers.register_status[register] = RegisterStatus.ALLOCATED
            register_count[register][1] = register
            
    for line in pseudo_code.split("\n"):
        split_line = line.split()
        if not split_line:
            print()
            continue
        if split_line[0] == "beq" or split_line[0] == "bne" or split_line[0] == "bgt" or split_line[0] == "blt" or split_line[0] == "b" or split_line[0] == "str" or split_line[0] == "ldr" or split_line[0] == "bl":
                print(line)
                continue
        for word in reversed(split_line):
            for register in register_count:
                regex = re.compile(r"\b" + register + r"\b")
                if regex.match(word):
                    if(register_count[register][1] == None):
                        allocated_reg = Registers.allocate_register()
                        register_count[register][1] = allocated_reg
                        line = re.sub(regex, " " + allocated_reg + " ", line)
                    else:
                        line = re.sub(regex, " " + register_count[register][1] + " ", line)
                    register_count[register][0] -= 1
                    if(register_count[register][0] == 0):
                        Registers.free_register(register_count[register][1])
                        register_count[register][1] = None
                    if(register_count[register][0] < 0):
                        print("ERROR: register count < 0")
                        exit(1)
                    break
        
        regex = re.compile(r"\b" + "notpush" + r"\b")
        if regex.findall(line):
            potential_push_registers = ["r0", "r1", "r2", "r3"]
            regex = re.compile(r"\b" + "r[0-9]" + r"\b")
            for register in re.findall(regex, line):
                try:
                    potential_push_registers.remove(register)
                except:
                    pass
            
            print("\tpush".ljust(10), " { ", end="")
            for register in potential_push_registers:
                print(register, end=" , ")
            print("}")
            continue
    
        regex = re.compile(r"\b" + "notpop" + r"\b")
        if regex.findall(line):
            potential_push_registers = ["r0", "r1", "r2", "r3"]
            regex = re.compile(r"\b" + "r[0-9]" + r"\b")
            for register in re.findall(regex, line):
                try:
                    potential_push_registers.remove(register)
                except:
                    pass
            
            print("\tpop".ljust(10), " { ", end="")
            for register in potential_push_registers:
                print(register, end=" , ")
            print("}")
            continue
        print(line)



def compile(code: str, program: Program) -> str:
    """Function compiles the program into CM0 code.

    Returns a string containing the compiled code, which can be written
    to an output file.

    args:
        code:  Code that is being lexed, parsed, and compiled.
        program: The AST of the program to compile
    
    returns:
        A string containing the compiled code.
    """
    pseudo_compiled_code = pseudo_compile(code, program)
    print(pseudo_compiled_code)
    
    


if __name__ == '__main__':
    # if len(sys.argv) < 2:
    #     print("Expected filename")
    #     exit()

    # with open("D:\\Nathan\\Bestanden\\ATP\\testfile.txt", "rb") as f:
    #     code = f.read().decode("utf-8")  
    with open("/home/nathan/Documents/ATP/random_functions.txt", "rb") as f:
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
    