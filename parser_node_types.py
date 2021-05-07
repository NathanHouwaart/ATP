from typing import *
from token_s import Token
from token_types import TokenTypes
from dataclasses import dataclass

@dataclass(frozen=True)
class Node:
    loc_: Dict[str, Dict[str,int]]
    range_: List[int]

@dataclass(frozen=True)
class Program(Node):
    body_: List['Node']
    
    def __repr__(self):
        ret = "Program:\n"
        ret += "\tloc_=" + str(self.loc_) + "\n"
        ret += "\trange_=" + str(self.range_) + "\n"
        ret += "\tbody_=["+"\n"
        for item in self.body_:
            ret+= str(item) + "\n\n"
        ret +="]"
        return ret
        
@dataclass(frozen=True)
class Identifier(Node):
    name_ : str

@dataclass(frozen=True)
class BlockStatement(Node):
    body_: List['Node']

@dataclass(frozen=True)
class FunctionDeclaration(Node):
    id_: Identifier
    params_: List[Identifier]
    body_: BlockStatement    

@dataclass(frozen=True)
class Literal(Node):
    value_: int
    raw_: str

@dataclass(frozen=True)
class IfStatement(Node):
    test_: Node
    consequent_: BlockStatement

@dataclass(frozen=True)
class WhileStatement(Node):
    test_: Node
    body_: BlockStatement

@dataclass(frozen=True)
class ReturnStatement(Node):
    argument_: Node

@dataclass(frozen=True)
class ExpressionStatement(Node):
    expression_: Node

@dataclass(frozen=True)
class CallExpression(Node):
    type_: str # multiply, add, divide, subtract
    left_: Node
    right_: Node

@dataclass(frozen=True)
class UnaryExpression(Node):
    operator_: str
    argument_: Literal

@dataclass(frozen=True)
class VariableDeclaration(Node):
    id_: str
    init_: Node

#####
#
# OLD Nodes
#
#####
class NumberNode():
    def __init__(self, token):
        self.token = token
        
    def __repr__(self):
        return f'{self.token}'

class VarriableAssignNode():
    def __init__(self, variable_name, expression):
        self.variable_name = variable_name
        self.expression = expression
        
    def __repr__(self):
        return f'{self.variable_name}, {self.expression}'

class UnaryOperator():
    def __init__(self, token, node):
        self.token = token
        self.node = node
    
    def __repr__(self):
        return f'({self.token}, {self.node})'

class BinaryOperator():
    def __init__(self, left, operator, right):
        self.left = left
        self.token = self.op = operator
        self.right = right
    
    def __repr__(self):
        return f'({self.left}, {self.token}, {self.right})'

class Num():
    def __init__(self, token: Token):
        self.token = token
        self.value = token.value

class Function():
    def __init__(self):
        self.children = []

class Assign():
    def __init__(self, left, operator, right):
        self.left = left
        self.token = self.op = op
        self.right = right
        
class Var():
    def __init__(self, token):
        self.token = token
        self.value = token.value

class NoOp():
    pass

