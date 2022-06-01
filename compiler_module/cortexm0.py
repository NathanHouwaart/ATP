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


###############################################################################    

def cm0_add(r1, r2, r3):
    print(f"\tadd".ljust(10), f"{r1}, {r2}, {r3}")
    return r1

def cm0_mul(r1, r2, r3):
    print(f"\tmul".ljust(10), f"{r1}, {r2}, {r3}")
    return r1

def cm0_sub(r1, r2, r3):
    print(f"\tsub".ljust(10), f"{r1}, {r2}, {r3}")
    return r1

def cm0_cmp(r1, r2):
    print(f"\tcmp".ljust(10), f"{r1}, {r2}")
    
def cm0_blt(label_name):
    print(f"\tblt".ljust(10), f"{label_name}")

def cm0_bgt(label_name):
    print(f"\tbgt".ljust(10), f"{label_name}")

def cm0_bne(label_name):
    print(f"\tbne".ljust(10), f"{label_name}")

def cm0_beq(label_name):
    print(f"\tbeq".ljust(10), f"{label_name}")

def cm0_or(r1, r2, r3):
    print(f"\torr".ljust(10), f"{r1}, {r2}, {r3}")

def cm0_and(r1, r2, r3):
    print(f"\tand".ljust(10), f"{r1}, {r2}, {r3}")

def cm0_mov(r1, r2):
    print(f"\tmov".ljust(10), f"{r1}, {r2}")

def cm0_movi(r1, value):
    print(f"\tmov".ljust(10), f"{r1}, #{value}")
    
def cm0_label(label_name):
    print(f"{label_name}:")


# def cm0_sub(r1, r2):
#     print(f"\tsub".ljust(10), f"{Registers.registers[r1]}, {Registers.registers[r1]}, {Registers.registers[r2]}")
#     Registers.free_register(r2)
#     # print(Registers.free)
#     return r1



def cm0_call(function_name):
    print(f"\tbl".ljust(10),  f"{function_name}")


def cm0_create_label(label_name):
    print(f"{label_name}:")


def cm0_function_preamble(stack_size):
    print("\tpush".ljust(10), "{lr}")
    if(stack_size):
        print("\tsub".ljust(10),  "sp, sp, #4")
        
    
def cm0_function_postamble(stack_size):
    if(stack_size):
        print("\tadd".ljust(10),  "sp, sp, #4")
    print("\tpop".ljust(10),  "{pc}")