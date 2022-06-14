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

# class CM0_Registers(Enum):
#     r0 = "r0"
#     r1 = "r1"
#     r2 = "r2"
#     r3 = "r3"
#     r4 = "r4"
#     r5 = "r5"
#     r6 = "r6"
#     r7 = "r7"


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


class CM0_Registers:
    def __init__(self) -> None:
        self.register_status = { 
            "r0": RegisterStatus.FREE, "r1":RegisterStatus.FREE, "r2":RegisterStatus.FREE, 
            "r3": RegisterStatus.FREE, "r4":RegisterStatus.FREE, "r5":RegisterStatus.FREE, 
            "r6": RegisterStatus.FREE, "r7":RegisterStatus.FREE}

        self.register_list = ["r0", "r1", "r2", "r3", "r4", "r4", "r6", "r7"]

    def free_all_registers(self):
        self.register_status = dict.fromkeys(self.register_status, RegisterStatus.FREE)
    
   
    def allocate_register(self):
        for register in self.register_status:
            if self.register_status[register] == RegisterStatus.FREE:
                self.register_status[register] = RegisterStatus.ALLOCATED
                return register
        print("No registers left")
        exit()
    
    
    def allocate_specific_register(self, register : str):
        if self.register_status[RegisterStatus.FREE]:
            self.register_status[register] = RegisterStatus.ALLOCATED
            return register
        print("Register {} is not free!".format(register))
        exit()
    
    
    def free_register(self, register: str):
        if(self.register_status[register] == RegisterStatus.FREE):    
            print("Register already free")
            exit()
        self.register_status[register] = RegisterStatus.FREE
        

    def has_free_registers(self):
        for register in self.register_status:
            if(self.register_status[register] == RegisterStatus.FREE):
                return True
        return False


    def allocate_register_range(self, start, end):
        for i in range(start, end):
            self.register_status[self.register_list[i]] = RegisterStatus.ALLOCATED


#############################################################################
##                       Cortex M0 Load And Store                          ##
#############################################################################

def cm0_str(
    pseudo_code: str, 
    r1: str, 
    stack_offset: int
) -> str:
    """Cortex-m0 store register instruction
    Stores the value of register r1 to the stack at the offset stack_offset

    Args:
        Pseudo code:    The pseudo code of the program
        r1:             The register to store
        stack_offset:   The offset from the stack pointer

    Returns:
        The pseudo code with the store instruction added
    """
    pseudo_code += f"\tstr".ljust(10) + f"{r1} , [ sp , #{stack_offset} ] \n"
    return pseudo_code


def cm0_ldr(
    pseudo_code: str, 
    r1: str, 
    stack_offset: int
) -> str:
    """Cortex-m0 load register instruction
    Loads the value of the stack at the offset stack_offset to register r1
    
    Args:
        Pseudo code:    The pseudo code of the program
        r1:             The register to load
        stack_offset:   The offset from the stack pointer

    Returns:
        The pseudo code with the load instruction added
    """
    pseudo_code += f"\tldr".ljust(10) + f"{r1} , [ sp, #{stack_offset} ] \n"
    return pseudo_code



#############################################################################
##                    Cortex M0 Arithmetic Instrictions                    ##
#############################################################################

def cm0_add(
    pseudo_code: str, 
    r1: str, 
    r2: str, 
    r3: str
) -> str:
    """Cortex-m0 add instruction
    Adds the values of registers r2 and r3 to register r1
    
    Args:
        pseudo_code:    The pseudo code of the program
        r1:             The register to store the result in
        r2:             Operand 1
        r3:             Operand 2

    Returns:
        The pseudo code with the add instruction added
    """
    pseudo_code += f"\tadd".ljust(10) + f"{r1} , {r2} , {r3} \n"
    return pseudo_code



def cm0_mul(
    pseudo_code: str, 
    r1: str, 
    r2: str, 
    r3: str
) -> str:
    """Cortex-m0 multiply instruction
    Multiplies the values of registers r2 and r3 and stores the result in register r1
    
    Args:
        pseudo_code:    The pseudo code of the program
        r1:             The register to store the result in
        r2:             Operand 1
        r3:             Operand 2

    Returns:
        The pseudo code with the multiply instruction added
    """
    pseudo_code += f"\tmul".ljust(10) + f"{r1} , {r2} , {r3} \n"
    return pseudo_code



def cm0_sub(
    pseudo_code: str, 
    r1: str, 
    r2: str, 
    r3: str
) -> str:
    """Cortex-m0 subtract instruction
    Subtracts the r3 from r2 and stores the result in register r1

    Args:
        pseudo_code:    The pseudo code of the program
        r1:             The register to store the result in
        r2:             Operand 1
        r3:             Operand 2

    Returns:
        The pseudo code with the subtract instruction added   
    """
    pseudo_code += f"\tsub".ljust(10) + f"{r1} , {r2} , {r3} \n"
    return pseudo_code



def cm0_or(    
    pseudo_code: str, 
    r1: str, 
    r2: str, 
    r3: str
) -> str:
    """Cortex-m0 bitwise or instruction
    Performs a bitwise or on the values of registers r2 and r3 and stores the result in register r1
    
    Args:
        pseudo_code:    The pseudo code of the program
        r1:             The register to store the result in
        r2:             Operand 1
        r3:             Operand 2

    """
    pseudo_code += f"\torr".ljust(10) + f"{r2} , {r2} , {r3} \n"
    pseudo_code = cm0_mov(pseudo_code, r1, r2)
    return pseudo_code


def cm0_and(
    pseudo_code: str, 
    r1: str, 
    r2: str, 
    r3: str
) -> str:
    """Cortex-m0 bitwise and instruction
    Performs a bitwise and on the values of registers r2 and r3 and stores the result in register r1

    Args:
        pseudo_code:    The pseudo code of the program
        r1:             The register to store the result in
        r2:             Operand 1
        r3:             Operand 2
    
    Returns:
        The pseudo code with the bitwise and instruction added
    """
    pseudo_code += f"\tand".ljust(10) + f"{r2} , {r2} , {r3} \n"
    pseudo_code = cm0_mov(pseudo_code, r1, r2)
    return pseudo_code


#############################################################################
##                     Cortex M0 Descision Instructions                    ##
#############################################################################

def cm0_cmp(
    pseudo_code: str, 
    r1: str, 
    r2: str
) -> str:
    """Cortex-m0 compare instruction
    Compares the values of registers r1 and r2 and sets the conditional flags
    
    Args:
        pseudo_code:    The pseudo code of the program
        r1:             The register to compare
        r2:             The register to compare
    
    Returns:
        The pseudo code with the compare instruction added
    """
    pseudo_code += f"\tcmp".ljust(10) + f"{r1} , {r2} \n"
    return pseudo_code



def cm0_blt(
    pseudo_code: str, 
    label_name: str
) -> str:
    """Cortex-m0 branch if less than instruction
    Branches to the label if the condition flag is less than

    Args:
        pseudo_code:    The pseudo code of the program
        label_name:     The name of the label to branch to

    Returns:
        The pseudo code with the branch if less than instruction added
    """
    pseudo_code += f"\tblt".ljust(10) + f"{label_name} \n"
    return pseudo_code



def cm0_bgt(
    pseudo_code: str, 
    label_name: str
) -> str:
    """Cortex-m0 branch if greater than instruction
    Branches to the label if the condition flag is greater than

    Args:
        pseudo_code:    The pseudo code of the program
        label_name:     The name of the label to branch to

    Returns:
        The pseudo code with the branch if greater than instruction added
    """
    pseudo_code += f"\tbgt".ljust(10) + f"{label_name} \n"
    return pseudo_code



def cm0_bne(
    pseudo_code: str, 
    label_name: str
) -> str:
    """Cortex-m0 branch if not equal instruction
    Branches to the label if the condition flag is not equal

    Args:
        pseudo_code:    The pseudo code of the program
        label_name:     The name of the label to branch to

    Returns:
        The pseudo code with the branch if not equal instruction added
    """
    pseudo_code += f"\tbne".ljust(10) + f"{label_name} \n"
    return pseudo_code



def cm0_beq(
    pseudo_code: str, 
    label_name: str
) -> str:
    """Cortex-m0 branch if equal instruction
    Branches to the label if the condition flag is equal
    
    Args:
        pseudo_code:    The pseudo code of the program
        label_name:     The name of the label to branch to
        
    Returns:
        The pseudo code with the branch if equal instruction added
    """
    pseudo_code += f"\tbeq".ljust(10) + f"{label_name} \n"
    return pseudo_code



def cm0_b(
    pseudo_code: str, 
    label_name: str
) -> str:
    """Cortex-m0 unconditional branch instruction

    Args:
        pseudo_code:    The pseudo code of the program
        label_name:     The name of the label to branch to
            
    Returns:
        The pseudo code with the unconditional branch instruction added
    """
    pseudo_code += f"\tb".ljust(10) + f"{label_name} \n"
    return pseudo_code



def cm0_call(
    pseudo_code: str,
    function_name: str
) -> str:
    """Cortex-m0 branch link instruction
    Branches to the label and saves the return address 

    Args:
        pseudo_code:    The pseudo code of the program
        function_name: The name of the function to call
    
    Returns:
        The pseudo code with the call instruction added
    """
    pseudo_code += f"\tbl".ljust(10) + f"{function_name} \n"
    return pseudo_code


#############################################################################
##                       Cortex M0 Misc Instructions                       ##
#############################################################################

def cm0_mov(
    pseudo_code: str, 
    r1: str, 
    r2: str
):
    """Cortex-m0 move instruction
    Moves the value of register r2 to register r1
    
    Args:
        pseudo_code:    The pseudo code of the program
        r1:             The register to store the result in
        r2:             The register to move the value from

    Returns:
        The pseudo code with the move instruction added
    """
    pseudo_code += f"\tmov".ljust(10) + f"{r1} , {r2} \n"
    return pseudo_code



def cm0_movi(
    pseudo_code: str, 
    r1: str, 
    value: int
) -> str:
    """Cortex-m0 move immediate instruction
    Moves the value to register r1

    Args:
        pseudo_code:    The pseudo code of the program
        r1:             The register to store the result in
        value:          The value to move to register r1

    Returns:
        The pseudo code with the move immediate instruction added
    """
    pseudo_code += f"\tmov".ljust(10) + f"{r1} , #{value} \n"
    return pseudo_code



def cm0_label(
    pseudo_code: str, 
    label_name: str
) -> str:
    """Creates a cortex-m0 assembly label
        
    Args:
        pseudo_code:    The pseudo code of the program
        label_name:     The name of the label to create

    Returns:
        The pseudo code with the label added
    """
    pseudo_code += f"{label_name}: \n"
    return pseudo_code



def cm0_function_preamble(
    pseudo_code: str,
    stack_size: int
) -> str:
    """Cortex-m0 function preamble
    Creates a function preamble
        
    Args:
        pseudo_code:    The pseudo code of the program
        stack_size:     The size of the stack to allocate
        
    Returns:
        The pseudo code with the function preamble added
    """

    pseudo_code += "\tpush".ljust(10) + "{ lr , r4 - r7 } \n"
    if(stack_size):
        pseudo_code += "\tsub".ljust(10) + "sp , sp , #{" + stack_size + "} \n"
    return pseudo_code
        
    
def cm0_function_postamble(
    pseudo_code: str,
    func_name: str, 
    stack_size: int
) -> str:
    """Cortex-m0 function postamble
    Creates a function postamble
    
    Args:
        pseudo_code:    The pseudo code of the program
        func_name:      The name of the function to create the postamble for
        stack_size:     The size of the stack to allocate
        
    Returns:
        The pseudo code with the function postamble added
    """
    pseudo_code = cm0_label(pseudo_code, f"{func_name}_end")
    if(stack_size):
        pseudo_code += "\tadd".ljust(10) + "sp , sp , #{" + stack_size + "} \n"
    pseudo_code += "\tpop".ljust(10) + "{ pc , r4 - r7 } \n\n"
    return pseudo_code



def cm0_global(
    pseudo_code: str,
    global_name: str
) -> str:
    """Cortex-m0 global symbol
    Creates a global symbol
        
    Args:
        pseudo_code:    The pseudo code of the program
        global_name:    The name of the global variable to create
        
    Returns:
        The pseudo code with the global variable added
    """
    pseudo_code += f".global {global_name} \n"
    return pseudo_code