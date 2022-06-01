



from typing import List
from arm_registers import Registers
from dataclasses import dataclass
import json

class CompilerDataStructure:
    push_registers : List[Registers]   = [] 
    preamble       : List[str]         = [] 
    postamble      : List[str]         = [] 
    body           : List[str]         = [] 
    
    def list_push_registers(self, string: str, registers: List[Registers]) -> str:
        if len(registers) == 0: 
            return string
        head, *tail = registers
        string +=  ", " + head.value[1]
        return self.list_push_registers(string, tail)
        
    def __repr__(self) -> str:
        return \
            f"""PUSH {{ lr{self.list_push_registers("", self.push_registers)} }}\n""" + \
            f"""POP {{ lr{self.list_push_registers("", self.push_registers)} }}\n"""

    
    