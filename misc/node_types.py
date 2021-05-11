from typing import *
from misc.token_types import *
from dataclasses import dataclass


@dataclass(frozen=True)
class Node:
    loc_: Dict[str, Dict[str,int]]
    range_: List[int]
    
    def pretty_print(self, spaces=4):
        returnstring = ""
        returnstring += spaces*" " + "loc_=" + str(self.loc_) + ",\n"
        returnstring += spaces*" " + "range_=" + str(self.range_) + ",\n" 
        return returnstring


@dataclass(frozen=True)
class Program(Node):
    body_: List['Node']
    
    def pretty_print(self, spaces=0):
        returnstring =  self.__class__.__name__ + "(\n"
        returnstring += super().pretty_print(spaces=spaces+4)
        returnstring += (spaces+4)*" " + "body_=["+"\n"
        for node in self.body_:
            returnstring += (spaces+8)*" " 
            returnstring += node.pretty_print(spaces=spaces+8)
        returnstring += (spaces+4)*" " + "],\n"
        returnstring += spaces*" " + "),\n"
        return returnstring

        
@dataclass(frozen=True)
class Identifier(Node):
    name_ : str
    
    def pretty_print(self, spaces=0):
        returnstring =  self.__class__.__name__ + "(\n"
        returnstring += super().pretty_print(spaces=spaces+4)
        returnstring += (spaces+4)*" " + "name_=" + str(self.name_) + "\n"
        returnstring += spaces*" " + "),\n"
        return returnstring


@dataclass(frozen=True)
class BlockStatement(Node):
    body_: List['Node']
    
    def pretty_print(self, spaces=0):
        returnstring =  self.__class__.__name__ + "(\n"
        returnstring += super().pretty_print(spaces=spaces+4)
        returnstring += (spaces+4)*" " + "body_=[" + "\n"
        for node in self.body_:
            returnstring += (spaces+8)*" " 
            returnstring += node.pretty_print(spaces=spaces+8)
        returnstring += (spaces+4)*" " + "],\n"
        returnstring += spaces*" " + "),\n"
        return returnstring


@dataclass(frozen=True)
class FunctionDeclaration(Node):
    id_: Identifier
    params_: List[Identifier]
    body_: BlockStatement
    
    def pretty_print(self, spaces=0):
        returnstring = self.__class__.__name__ + "(\n"
        returnstring += super().pretty_print(spaces=spaces+4)
        returnstring += (spaces+4)*" " + "id_=" + str(self.id_) + ",\n"
        returnstring += (spaces+4)*" " + "params_=[" + "\n"
        for node in self.params_:
            returnstring += (spaces+8)*" " 
            returnstring += node.pretty_print(spaces=spaces+8)
        returnstring += (spaces+4)*" " + "],\n"
        returnstring += (spaces+4)*" " + "body_=" + self.body_.pretty_print(spaces=spaces+4)
        returnstring += spaces*" " + "),\n"
        return returnstring    


@dataclass(frozen=True)
class Literal(Node):
    value_: int
    raw_: str
    
    def pretty_print(self, spaces=0):
        returnstring = self.__class__.__name__ + "(\n"
        returnstring += super().pretty_print(spaces=spaces+4)
        returnstring += (spaces+4)*" " + "value_=" + str(self.value_) + ",\n"
        returnstring += (spaces+4)*" " + "raw_=" + str(self.raw_) + "\n"
        returnstring += spaces*" " + "),\n"
        return returnstring
    

@dataclass(frozen=True)
class IfStatement(Node):
    test_: Node
    consequent_: BlockStatement
    alternate_: Optional['IfStatement']

    def pretty_print(self, spaces=0):
        returnstring =  self.__class__.__name__ + "(\n"
        returnstring += super().pretty_print(spaces=spaces+4)
        returnstring += (spaces+4)*" " + "test_=" + self.test_.pretty_print(spaces=spaces+4)
        returnstring += (spaces+4)*" " + "consequent_=" + self.consequent_.pretty_print(spaces=spaces+4)
        returnstring += (spaces+4)*" " + "alternate_=" + (self.alternate_.pretty_print(spaces=spaces+4) if self.alternate_ else "[]\n")
        returnstring += spaces*" " + "),\n"
        return returnstring


@dataclass(frozen=True)
class WhileStatement(Node):
    test_: Node
    body_: BlockStatement


@dataclass(frozen=True)
class ReturnStatement(Node):
    argument_: Node

    def pretty_print(self, spaces=0):
        returnstring =  self.__class__.__name__ + "(\n"
        returnstring += super().pretty_print(spaces=spaces+4)
        returnstring += (spaces+4)*" " + "argument_=" + self.argument_.pretty_print(spaces=spaces+4)
        returnstring += spaces*" " + "),\n"
        return returnstring


@dataclass(frozen=True)
class ExpressionStatement(Node):
    expression_: Node
    
    def pretty_print(self, spaces=0):
        returnstring =  self.__class__.__name__ + "(\n"
        returnstring += super().pretty_print(spaces=spaces+4)
        returnstring += (spaces+4)*" " + "expression_=" + self.expression_.pretty_print(spaces=spaces+4)
        returnstring += spaces*" " + "),\n"
        return returnstring


@dataclass(frozen=True)
class CallExpression(Node):
    arguments_: List[Node]
    callee_ : Identifier
    
    def pretty_print(self, spaces=0):
        returnstring =  self.__class__.__name__ + "(\n"
        returnstring += super().pretty_print(spaces=spaces+4)
        returnstring += (spaces+4)*" " + "arguments_=[" + "\n"
        for node in self.arguments_:
            returnstring += (spaces+8)*" " 
            returnstring += node.pretty_print(spaces=spaces+8)
        returnstring += (spaces+4)*" " + "callee_=" + self.callee_.pretty_print(spaces=spaces+4)
        returnstring += spaces*" " + "),\n"
        return returnstring


@dataclass(frozen=True)
class UnaryExpression(Node):
    operator_: str
    argument_: Literal

    def pretty_print(self, spaces=0):
        returnstring =  self.__class__.__name__ + "(\n"
        returnstring += super().pretty_print(spaces=spaces+4)
        returnstring += (spaces+4)*" " + "operator_=" + str(self.operator_) + "\n"
        returnstring += (spaces+4)*" " + "argument_=" + self.argument_.pretty_print(spaces=spaces+4)
        returnstring += spaces*" " + "),\n"
        return returnstring


@dataclass(frozen=True)
class VariableDeclaration(Node):
    id_: str
    init_: Node
    
    def pretty_print(self, spaces=0):
        returnstring =  self.__class__.__name__ + "(\n"
        returnstring += super().pretty_print(spaces=spaces+4)
        returnstring += (spaces+4)*" " + "id_=" + str(self.id_) + "\n"
        returnstring += (spaces+4)*" " + "init_=" + self.init_.pretty_print(spaces=spaces+4)
        returnstring += spaces*" " + "),\n"
        return returnstring


@dataclass(frozen=True)
class BinaryExpression(Node):
    operator_ : str
    left_: Node
    right_: Node
    
    def pretty_print(self, spaces=0):
        returnstring =  self.__class__.__name__ + "(\n"
        returnstring += super().pretty_print(spaces=spaces+4)
        returnstring += (spaces+4)*" " + "operator_=" + str(self.operator_) + "\n"
        returnstring += (spaces+4)*" " + "left_=" + self.left_.pretty_print(spaces=spaces+4)
        returnstring += (spaces+4)*" " + "right_=" + self.right_.pretty_print(spaces=spaces+4)
        returnstring += spaces*" " + "),\n"
        return returnstring