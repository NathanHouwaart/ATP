from typing import *
from token import Token
from token_types import TokenTypes

class Node(NamedTuple):
    loc_: Dict[str, Dict[str,int]]
    range_: List[int]

class Program(Node):
    body_: List['Node']

class Identifier(Node):
    name_ : str

class BlockStatement(Node):
    body_: List['Node']

class FunctionDeclaration(Node):
    id_: Identifier
    params_: List[Identifier]
    body_: BlockStatement    
    
class Literal(Node):
    value_: int
    raw_: str

class IfStatement(Node):
    test_: Node
    consequent_: BlockStatement

class WhileStatement(Node):
    test_: Node
    body_: BlockStatement
       
class ReturnStatement(Node):
    argument_: Node
        
class ExpressionStatement(Node):
    expression_: Node
    
class CallExpression(Node):
    type_: str # multiply, add, divide, subtract
    left_: Node
    right_: Node

class UnaryExpression(Node):
    operator_: str
    argument_: Literal

class VariableDeclaration(Node):
    kind_: str
    id_: str
    init: Node

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

