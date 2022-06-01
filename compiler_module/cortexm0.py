import sys
import os
import time
from itertools import islice

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from misc.symbol_table import SymbolTable

class Registers:
    registers = ["r0", "r1", "r2", "r3"]
    free      = [True, True, True, True]      
    
    @staticmethod
    def free_all_registers():
        for i in Registers.free:
            Registers.free[i] = True
    
    @staticmethod
    def allocate_register():
        for i in range(len(Registers.free)):
            if Registers.free[i]:
                Registers.free[i] = False
                return i
        print("No registers left")
        exit()
    
    @staticmethod
    def allocate_specific_register(register):
        if Registers.free[register]:
            Registers.free[register] = False
            return register
        print("Register {} is not free!".format(register))
        exit()
    
    @staticmethod
    def free_register(reg):
        if(Registers.free[reg] == True):    
            print("Register already free")
            exit()
        Registers.free[reg] = True
        
    @staticmethod
    def allocate_register_range(start, end):
        for i in range(start, end):
            Registers.free[i] = False
            
    @staticmethod
    def has_free_registers():
        return Registers.free.count(True) > 0


# Cortex-M0 assembly functions

def cm0_preamble():
    Registers.free_all_registers()
    print("main:")
    print("\tpush".ljust(10), "{r7, lr}")
    print("\tadd".ljust(10),  "r7, sp, #0")
    

def cm0_postamble():
    print("\tmov".ljust(10), "sp, r7")
    print("\tpop".ljust(10), "{r7, pc}")


def cm0_store(r1, stack_offset):
    """
    Pushes a registger to the stack
    """
    print(f"\tstr".ljust(10), f"{Registers.registers[r1]}, [sp, #{stack_offset}]")
    Registers.free_register(r1)
    

def cm0_load(stack_offset):
    """
    Pops a register from the stack and allocates it to a register
    """
    # if(Registers.free[preferred_register]):
    #     Registers.allocate_specific_register(preferred_register)
    #     print(f"\tldr".ljust(10), f"{Registers.registers[preferred_register]}, [sp, #{stack_offset}]")
    #     return preferred_register
    # else:
    reg = Registers.allocate_register()
    print(f"\tldr".ljust(10), f"{Registers.registers[reg]}, [sp, #{stack_offset}]")
    return reg

def cm0_movi(value):
    # Get a free register
    reg = Registers.allocate_register()
    # print(Registers.free)
    print(f"\tmov".ljust(10), f"{Registers.registers[reg]}, #{value}")
    return reg


def cm0_mov(r1, r2):
    print(f"\tmov".ljust(10), f"{Registers.registers[r1]}, {Registers.registers[r2]}")

def cm0_add(r1, r2, r3):
    print(f"\tadd".ljust(10), f"{Registers.registers[r1]}, {Registers.registers[r2]}, {Registers.registers[r3]}")
    

def cm0_add(r1, r2):
    print(f"\tadd".ljust(10), f"{Registers.registers[r1]}, {Registers.registers[r1]}, {Registers.registers[r2]}")
    Registers.free_register(r2)
    # print(Registers.free)
    return r1

def cm0_sub(r1, r2):
    print(f"\tsub".ljust(10), f"{Registers.registers[r1]}, {Registers.registers[r1]}, {Registers.registers[r2]}")
    Registers.free_register(r2)
    # print(Registers.free)
    return r1

def cm0_mul(r1, r2):
    print(f"\tmul".ljust(10), f"{Registers.registers[r1]}, {Registers.registers[r1]}, {Registers.registers[r2]}")
    Registers.free_register(r2)
    # print(Registers.free)
    return r1


def cm0_call(function_name):
    print(f"\tbl".ljust(10),  f"{function_name}")


def cm0_create_label(label_name):
    print(f"{label_name}:")

def cm0_div(r1, r2, symbol_table: SymbolTable):
    """
    Function generates a Cortex M0 ASM Divide instruction.
    
    Args:
        r1                  : Register which holds the numerator; Register to store the result in
        r2                  : Register which holds the denominator

    Returns:
        If no errors occured:
            - An AST in the form of a program node
            - An EOF Token
        If a grammar error occured:
            Raises a Syntax Error with a message of where the error occured
    """
    if r1 == 0 and r2 == 1:
        print(f"\tbl".ljust(10),  f"__aeabi_idiv")
        Registers.free_register(r2)
        return r1
    elif r1 == 0 and r2 != 1:
        if(not Registers.free[1]): # if r1 is not free
            print("load r1 to stack")
            print(f"\tmov".ljust(10), f"r1, {Registers.registers[r2]}")
            Registers.free_register(r2)
        else:
            print(f"\tmov".ljust(10), f"r1, {Registers.registers[r2]}")
            Registers.allocate_specific_register(1)
            Registers.free_register(r2)
    elif r1 != 0 and r2 == 1:
        if(not Registers.free[0]): # if r0 is not free
            print("load r1 to stack")
            print(f"\tmov".ljust(10), f"r0, {Registers.registers[r2]}")
            Registers.free_register(r1)
        else:
            print(f"\tmov".ljust(10), f"r0, {Registers.registers[r2]}")
            Registers.allocate_specific_register(0)
            Registers.free_register(r1)
    elif r1 == 1 and r2 == 0:
        print("hts")
        return r1

    if r1 != 0:
        print("\tmov".ljust(10), f"r0, {Registers.registers[r1]}")
        Registers.allocate_specific_register(0)
        Registers.free_register(r1)
    if r2 != 1:
        print("\tmov".ljust(10), f"r1, {Registers.registers[r2]}")
        Registers.free_register(r2)
        
    print(f"\tbl".ljust(10),  f"__aeabi_idiv")
    # print(Registers.free)
    return 0


def cm0_function_preamble(stack_size):
    print("\tpush".ljust(10), "{lr}")
    if(stack_size):
        print("\tsub".ljust(10),  "sp, sp, #4")
        
    
def cm0_function_postamble(stack_size):
    if(stack_size):
        print("\tadd".ljust(10),  "sp, sp, #4")
    print("\tpop".ljust(10),  "{pc}")