from enum import Enum


class Registers(Enum):
# Scratch registers
    R0  =   0,"r0"
    R1  =   1,"r1"
    R2  =   2,"r2"
    R3  =   3,"r3"
    
# Preserved registers
    R4  =   4,"r4"
    R5  =   5,"r5"
    R6  =   6,"r6"
    R7  =   7,"r7"
    STACK = 8,"stack"

# # Possibly not used
#     R8  =   8,"r8"
#     R9  =   9,"r9"
#     R10 =   10,"r10"
#     R11 =   11,"r11"
#     R12 =   12,"r12"