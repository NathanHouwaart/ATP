from enum import Enum
import sys
import os
import time
from itertools import islice

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from misc.symbol_table import SymbolTable

class RegisterStatus(Enum):
    FREE = 0
    ALLOCATED = 1

class CM0_Registers(Enum):
    r0 = "r0"
    r1 = "r1"
    r2 = "r2"
    r3 = "r3"
    r4 = "r4"
    r5 = "r5"
    r6 = "r6"
    r7 = "r7"


class Registers:
    register_status = { 
        "r0": RegisterStatus.FREE, "r1":RegisterStatus.FREE, "r2":RegisterStatus.FREE, 
        "r3": RegisterStatus.FREE, "r4":RegisterStatus.FREE, "r5":RegisterStatus.FREE, 
        "r6": RegisterStatus.FREE, "r7":RegisterStatus.FREE}

    register_list = ["r0", "r1", "r2", "r3", "r4", "r4", "r6", "r7"]
    
    @staticmethod
    def free_all_registers():
        Registers.register_status = dict.fromkeys(Registers.register_status, RegisterStatus.FREE)
    
    @staticmethod
    def allocate_register():
        for register in Registers.register_status:
            if Registers.register_status[register] == RegisterStatus.FREE:
                Registers.register_status[register] = RegisterStatus.ALLOCATED
                return register
        print("No registers left")
        exit()
    
    @staticmethod
    def allocate_specific_register(register : str):
        if Registers.register_status[RegisterStatus.FREE]:
            Registers.register_status[register] = RegisterStatus.ALLOCATED
            return register
        print("Register {} is not free!".format(register))
        exit()
    
    @staticmethod
    def free_register(register: str):
        if(Registers.register_status[register] == RegisterStatus.FREE):    
            print("Register already free")
            exit()
        Registers.register_status[register] = RegisterStatus.FREE
        
    @staticmethod
    def has_free_registers():
        for register in Registers.register_status:
            if(Registers.register_status[register] == RegisterStatus.FREE):
                return True
        return False

    @staticmethod
    def allocate_register_range(start, end):
        for i in range(start, end):
            Registers.register_status[Registers.register_list[i]] = RegisterStatus.ALLOCATED


# Cortex-M0 assembly functions

def cm0_preamble():
    Registers.free_all_registers()
    print("main:")
    print("\tpush".ljust(10), "{r7, lr}")
    print("\tadd".ljust(10),  "r7, sp, #0")
    

def cm0_postamble():
    print("\tmov".ljust(10), "sp, r7")
    print("\tpop".ljust(10), "{r7, pc}")



###############################################################################    

def cm0_str(r1, stack_offset):
    print(f"\tstr".ljust(10), f"{r1} , [sp, #{stack_offset}]")

def cm0_ldr(r1, stack_offset):
    print(f"\tldr".ljust(10), f"{r1} , [sp, #{stack_offset}]")

def cm0_add(r1, r2, r3):
    print(f"\tadd".ljust(10), f"{r1} , {r2} , {r3} ")
    return r1

def cm0_mul(r1, r2, r3):
    print(f"\tmul".ljust(10), f"{r1} , {r2} , {r3} ")
    return r1

def cm0_sub(r1, r2, r3):
    print(f"\tsub".ljust(10), f"{r1} , {r2} , {r3} ")
    return r1

def cm0_cmp(r1, r2):
    print(f"\tcmp".ljust(10), f"{r1} , {r2} ")
    
def cm0_blt(label_name):
    print(f"\tblt".ljust(10), f"{label_name} ")

def cm0_bgt(label_name):
    print(f"\tbgt".ljust(10), f"{label_name} ")

def cm0_bne(label_name):
    print(f"\tbne".ljust(10), f"{label_name} ")

def cm0_beq(label_name):
    print(f"\tbeq".ljust(10), f"{label_name} ")

def cm0_or(r1, r2, r3):
    print(f"\torr".ljust(10), f"{r1} , {r2} , {r3} ")

def cm0_and(r1, r2, r3):
    print(f"\tand".ljust(10), f"{r2} , {r2} , {r3} ")
    cm0_mov(r1, r2)

def cm0_mov(r1, r2):
    print(f"\tmov".ljust(10), f"{r1} , {r2} ")

def cm0_movi(r1, value):
    print(f"\tmov".ljust(10), f"{r1} , #{value} ")
    
def cm0_label(label_name):
    print(f"{label_name}:")

def cm0_b(label_name):
    print(f"\tb".ljust(10), f"{label_name} ")

def cm0_return():
    print("\tpop".ljust(10),  "{pc}")
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
    print("\tpush".ljust(10), "{ lr , r4 - r7 }")
    if(stack_size):
        print("\tsub".ljust(10),  "sp , sp , #4")
        
    
def cm0_function_postamble(func_name, stack_size):
    cm0_label(f"{func_name}_end")
    if(stack_size):
        print("\tadd".ljust(10),  " sp , sp , #4")
    print("\tpop".ljust(10),  "{ pc , r4 - r7 }")
    print()
    print()