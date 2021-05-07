from typing import *
from dataclasses import dataclass
from parser_node_types import *

@dataclass(frozen=True)
class Node:
    loc_: Dict[str, Dict[str,int]]
    range_: List[int]

@dataclass(frozen=True)
class Program(Node):
    body_: List['Node']
    
@dataclass(frozen=True)
class VariableDeclaration(Node):
    id_: str
    init_: Node

print(Program(loc_=[], range_={}, body_=[]))
print(VariableDeclaration(loc_=[], range_={}, id_=[], init_=" "))
