from calendar import c
from subprocess import call
import sys
import os
import time

from defer import return_value
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
from arm_registers import *
from compiler_data_structures import *       
from cortexm0 import *

RETURN_REGISTER = "r0"
CMP_I_REGISTER  = "r4"


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------  Helper Functions ------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

counter = 0

def get_attribute(method_name, default):
    if method_name in globals():
        return globals()[method_name]
    return default

def no_compile_method(code: str, node: Node, symbol_table: SymbolTable, call_stack: List[Node]):
    print("no compile method for node type", type(node))
    exit()
    return symbol_table

def calculate_num_nodes(code: str, node: Node, symbol_table: SymbolTable):
    if(type(node) == BinaryExpression):
        left = 1 + calculate_num_nodes(code, node.left_, symbol_table)
        right = 1 + calculate_num_nodes(code, node.right_, symbol_table)
        if(right > left):
            return right
        else:
            return left
    else:
        return 1


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------  Compile Functions -----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

def compile_CallExpression(code: str, node: CallExpression, symbol_table: SymbolTable, call_stack: List[Node]):
    # print("compile_CallExpression")
    # 1. Check if function is defined
    # symbol_info = symbol_table_get(symbol_table, node.callee_.name_)
    # if symbol_info == None:
    #     generate_error_message(node, code, "Undefined function", True)
    
    return_value, symbol_table = symbol_table_get_and_del_return_symbol(compile_loop(code, node.arguments_, symbol_table, call_stack + [node]))
    print("\tnotpush".ljust(10), "{ " + return_value[0].symbol_register + " }")
    cm0_mov("r0", return_value[0].symbol_register)
    cm0_call(node.callee_.name_)
    cm0_mov(return_value[0].symbol_register, "r0")
    print("\tnotpop".ljust(10), "{ " + return_value[0].symbol_register + " }")
    if(type(call_stack[-1]) == VariableDeclaration):
        cm0_mov(call_stack[-1].id_ + "_reg", return_value[0].symbol_register)

    symbol_table = symbol_table_add_return_symbol(symbol_table, return_value[0])
    return symbol_table


def add_function_arguments_to_symbol_table(symbol_table: SymbolTable, arguments: List[Literal], register_loc = 0):
    if len(arguments) == 0:
        return symbol_table
    
    head, *tail = arguments
    
    # Check if symbol is already defined. In that case, function has duplicate argument names
    if symbol_table_symbol_exists(symbol_table, head.name_):
        generate_error_message(head, code, "Duplicate function argument", True)
        
    # If not, add argument to symbol table
    symbol_table = symbol_table_set(symbol_table, head.name_ , VairableSymbol(head.name_, SymbolType.ARGUMENT, "r{}".format(register_loc)))
    return add_function_arguments_to_symbol_table(symbol_table, tail, register_loc + 1)



def compile_FunctionDeclaration(code: str, node: FunctionDeclaration, symbol_table: SymbolTable, call_stack):
    # print("compile_FunctionDeclaration")
    
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
    # Registers.allocate_register_range(0, len(node.params_))

    # 7. Write assebmly code for function
    print(".global ", node.id_)
    cm0_create_label(node.id_)                                                                      # Create label for branch
    cm0_function_preamble(0)                                                                        # Write function preamble
    function_symbol_table = compile_loop(code, [node.body_], function_symbol_table, call_stack + [node])     # Compile function body
    cm0_function_postamble(node.id_, 0)                                                                       # Write function postamble
    
    return symbol_table



def compile_ReturnStatement(code: str, node: ReturnStatement, symbol_table: SymbolTable, call_stack : List[Node]):
    # print("compile_ReturnStatement")
    result, symbol_table = symbol_table_get_and_del_return_symbol(compile_loop(code, [node.argument_], symbol_table, call_stack + [node]))
    cm0_mov("r0", result[0].symbol_register)
    # print("\n\n\n\n")
    if(type(call_stack[0]) == FunctionDeclaration and check_present(call_stack, IfStatement)):
        cm0_b(call_stack[0].id_ + "_end")
    return symbol_table

def check_present(arr, what):
    if(len(arr) == 0):
        return 0
    
    head, *tail = arr
    if(type(head) == what):
        return 1 + check_present(tail, what)
    return check_present(tail, what)
    

# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------  Compile Other stf -----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

def compile_BlockStatement(code: str, node: BlockStatement, symbol_table: SymbolTable, call_stack):
    # print("compile_BlockStatement")
    return compile_loop(code, node.body_, symbol_table, call_stack + [node])


def compile_BinaryExpression(code: str, node: BinaryExpression, symbol_table: SymbolTable, call_stack: Node):
    # print("compile_BinaryExpression")
    operator = node.operator_

    # Check which node to walk first: deepest node goes first in order to minimize stack usage    
    left = calculate_num_nodes(code, node.left_, symbol_table)
    right = calculate_num_nodes(code, node.right_, symbol_table)
    
    if(left > right):
        left , symbol_table = symbol_table_get_and_del_return_symbol(compile_loop(code, [node.left_], symbol_table, call_stack + [node]))
        right, symbol_table = symbol_table_get_and_del_return_symbol(compile_loop(code, [node.right_], symbol_table, call_stack + [node]))       
    else:
        right, symbol_table = symbol_table_get_and_del_return_symbol(compile_loop(code, [node.right_], symbol_table, call_stack + [node]))
        left , symbol_table = symbol_table_get_and_del_return_symbol(compile_loop(code, [node.left_], symbol_table, call_stack + [node]))
    right = right[0]
    left  = left[0]
    # print(right, left)


    if(type(call_stack[-1]) == VariableDeclaration):
        result_reg_name = call_stack[-1].id_ + "_reg"
    elif(type(call_stack[-1]) == ReturnStatement):
        result_reg_name = "function_return" + "_reg"
    else:
        result_reg_name = right.symbol_name + "_" + left.symbol_name + "_res" + "_reg"
    
    if operator == TokenTypes.PLUS:
        result_register = cm0_add(result_reg_name,  right.symbol_register, left.symbol_register)
        symbol_table_add_return_symbol(symbol_table, VairableSymbol(result_register, SymbolType.VARIABLE, result_register))
    elif operator == TokenTypes.MINUS: 
        result_register = cm0_sub(result_reg_name,  left.symbol_register, right.symbol_register)
        symbol_table_add_return_symbol(symbol_table, VairableSymbol(result_register, SymbolType.VARIABLE, result_register))
        # elif operator == TokenTypes.DIVIDE        : symbol_table_add_return_symbol(symbol_table, cm0_div(left[0], right[0], symbol_table))
    elif operator == TokenTypes.MULTIPLY: 
        result_register = cm0_mul(result_reg_name,  right.symbol_register, left.symbol_register)
        symbol_table_add_return_symbol(symbol_table, VairableSymbol(result_register, SymbolType.VARIABLE, result_register))
    elif operator == TokenTypes.IS_EQUAL:
        branch_label_name = right.symbol_name + "_eq_" + left.symbol_name + "_res_equal"
        cm0_movi(result_reg_name, 1)
        cm0_cmp(right.symbol_register, left.symbol_register)
        cm0_beq(branch_label_name)
        cm0_movi(result_reg_name, 0)
        cm0_label(branch_label_name)
        result_register = result_reg_name
        symbol_table_add_return_symbol(symbol_table, VairableSymbol(result_register, SymbolType.VARIABLE, result_register))        
    elif operator == TokenTypes.GREATER_THAN  : 
        branch_label_name = right.symbol_name + "_gt_" + left.symbol_name + "_res_greater_than"
        cm0_movi(result_reg_name, 1)
        cm0_cmp(left.symbol_register, right.symbol_register)
        cm0_bgt(branch_label_name)
        cm0_movi(result_reg_name, 0)
        cm0_label(branch_label_name)
        result_register = result_reg_name
        symbol_table_add_return_symbol(symbol_table, VairableSymbol(result_register, SymbolType.VARIABLE, result_register))        
    elif operator == TokenTypes.SMALLER_THAN  : 
        branch_label_name = right.symbol_name + "_lt_" + left.symbol_name + "_res_less_than"
        cm0_movi(result_reg_name, 1)
        cm0_cmp(left.symbol_register, right.symbol_register)
        cm0_blt(branch_label_name)
        cm0_movi(result_reg_name, 0)
        cm0_label(branch_label_name)
        result_register = result_reg_name
        symbol_table_add_return_symbol(symbol_table, VairableSymbol(result_register, SymbolType.VARIABLE, result_register))        

    elif operator == TokenTypes.AND:
        result_register = cm0_and(result_reg_name,  right.symbol_register, left.symbol_register)
        symbol_table_add_return_symbol(symbol_table, VairableSymbol(result_register, SymbolType.VARIABLE, result_register))
    elif operator == TokenTypes.OR: 
        result_register = cm0_or(result_reg_name,  right.symbol_register, left.symbol_register)
        symbol_table_add_return_symbol(symbol_table, VairableSymbol(result_register, SymbolType.VARIABLE, result_register))
     
    return symbol_table

def compile_IfStatement(code: str, node: Identifier, symbol_table: SymbolTable, call_stack: List[Node]):
    # print("compile_IfStatement")
    if_end_label = call_stack[0].id_ + "_if_end_" + str(check_present(call_stack, IfStatement)) + "_" + node_range_to_label(node)
    test_result, symbol_table = symbol_table_get_and_del_return_symbol(compile_loop(code, [node.test_], symbol_table, call_stack + [node]))
    cm0_cmp(test_result[0].symbol_register, "#0")
    if type(call_stack[0]) == FunctionDeclaration:
        branch_label = call_stack[0].id_ + "_if_false_" + str(check_present(call_stack, IfStatement)) + "_" + node_range_to_label(node)
        if node.alternate_:
            cm0_beq(branch_label)
        else:
            cm0_beq(if_end_label)    
    else:
        raise Exception("Code outside of function not supported")
    test_result, symbol_table = symbol_table_get_and_del_return_symbol(compile_loop(code, [node.consequent_], symbol_table, call_stack + [node]))
    if(node.alternate_):
        cm0_b(if_end_label)
        cm0_label(branch_label)
        test_result, symbol_table = symbol_table_get_and_del_return_symbol(compile_loop(code, [node.alternate_], symbol_table, call_stack + [node] ))
        cm0_label(if_end_label)
    else:
        cm0_label(if_end_label)
    return symbol_table

def present(arr, v): 
    return arr.count(v)

def node_range_to_label(node: Node):
    return str(node.range_[0]) + "_" + str(node.range_[1])

def compile_Identifier(code: str, node: Identifier, symbol_table: SymbolTable, call_stack):    
    # 1. Check if identifier is defined
    symbol = symbol_table_get(symbol_table, node.name_)                            # Get information from symbol table
    if symbol == None:                                                             # If not defined
        generate_error_message(node, code, f"{node.name_} is not defined", True)        # Generate error message
        
    symbol_table_add_return_symbol(symbol_table, symbol)
    return symbol_table


def compile_VariableDeclaration(code: str, node: VariableDeclaration, symbol_table: SymbolTable, call_stack):
    # print("compile_VariableDeclaration")
    # 2. Check if variable is already defined
    symbol = symbol_table_get(symbol_table, node.id_)                                   # Get information from symbol table
    if symbol != None and type(symbol) != VairableSymbol:                               # If a symbol is found, check if it is a variable
        generate_error_message(node, code, f"Redefinition of {node.id_}", True)         # If not, generate error

    # 1. Initialize variable
    symbol_table = compile_loop(code, [node.init_], symbol_table, call_stack + [node])                       # Compile the initializer 
    return_symbol, symbol_table = symbol_table_get_and_del_return_symbol(symbol_table)  # Get the register that the initializer is stored in
    return_symbol = return_symbol[0]                                                    # Get the register number         
    
    
    # # 4a. if variable is already defined
    # if symbol != None:                                                             # If a symbol is found, ask information about the symbol
        
    
    # # 4b. if variable is not defined. define it
    # else:
    symbol_table = symbol_table_set(symbol_table, node.id_, 
                                    VairableSymbol(node.id_, SymbolType.VARIABLE, node.id_ + "_reg"))     # Add new variable to symbol table with stack offset
    return symbol_table
 
 
 
def compile_Literal(code: str, node: Literal, symbol_table: SymbolTable, call_stack):
    if(type(call_stack[-1]) == VariableDeclaration):
        literal_id = call_stack[-1].id_
    else:
        literal_id = "literal_value_" + node.raw_ + "_" + node_range_to_label(node)
    cm0_movi(literal_id + "_reg", node.value_)
    symbol = LiteralSymbol(literal_id, SymbolType.LITERAL, literal_id + "_reg")
    symbol_table = symbol_table_set(symbol_table, literal_id, symbol)
    symbol_table = symbol_table_add_return_symbol(symbol_table, symbol)
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

def regnames_count(code, register_count: Dict[str, int]):
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

def format_pseudo_output(psuedo_output: str):
    formatted_psuedo_output = []
    for line in psuedo_output.split("\n"):
        if(line == "" or ":" in line or re.findall(r"\blr\b", line) or re.findall(r"\bpc\b", line)):
            continue
        line = line.replace(',', ' ').split()
        if line[0] ==  "beq" or line[0] ==  "b"  or line[0] == "bne" or line[0] == line or line[0] == "bgt" or line[0] == "blt" or line[0] == "str" or line[0] == "ldr" or line[0] == "bl" or line[0] == ".global":
            continue
        formatted_psuedo_output.append(line)
    return formatted_psuedo_output

def compile(code, program: Program):
    symbol_table = SymbolTable(symbols={}, parent=None, return_symbols=[], return_stop=False, stack_variables=0)
    symbol_table = symbol_table_set(symbol_table, "🖨", FunctionSymbol("__aeabi_idiv", SymbolType.FUNCTION, 1))
    
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    symbol_table = compile_loop(code, program.body_, symbol_table, [])
    pseudo_output = new_stdout.getvalue()
    sys.stdout = old_stdout
    
    print(pseudo_output)
    formatted_pseudo_output = format_pseudo_output(pseudo_output)
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
            
    for line in pseudo_output.split("\n"):
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
            potential_push_registers.remove(re.findall(regex, line)[0])
            
            print("\tpush".ljust(10), " { ", end="")
            for register in potential_push_registers:
                print(register, end=" , ")
            print("}")
            continue
    
        regex = re.compile(r"\b" + "notpop" + r"\b")
        if regex.findall(line):
            potential_push_registers = ["r0", "r1", "r2", "r3"]
            regex = re.compile(r"\b" + "r[0-9]" + r"\b")
            potential_push_registers.remove(re.findall(regex, line)[0])
            
            print("\tpop".ljust(10), " { ", end="")
            for register in potential_push_registers:
                print(register, end=" , ")
            print("}")
            continue
        print(line)


            
    
    
    # remove all empty lines
    
    # remove pop and push
    
    


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
    