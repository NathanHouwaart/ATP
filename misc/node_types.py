"""
@file node_types.py
@author Nathan Houwaart (nathan.houwaart@student.hu.nl)
@brief This file contains all parser node types
@version 0.1
@date 11-05-2021
"""

from typing import Optional, Dict, List, Union
from misc.token_types import *
from dataclasses import dataclass
import json

@dataclass(frozen=True)
class Node:
    """
    Base Node class

    ...

    Attributes
    ----------
    loc_ : Dict[str, Dict[str,int]]
        A dictionary containing two keys: start, end. Which in their turn contain
        another dictionary which also holds two keys: line, index. Their values are 
        the line and indexes where the node starts and ends.
    range_ : List[int]
        a list containing two items. The 0'th index contains the start index of the 
        node. The 1'st index contains the end index of the node. This index is document
        wide.

    Methods
    -------
    jsonify(spaces=4)
        returns a json like string to print out the node into a json format.
    """
    loc_: Dict[str, Dict[str,int]]
    range_: List[int]
    
    def jsonify(self, spaces=4):
        returnstring = ""
        returnstring += spaces*" " + "\"loc_\":" + json.dumps(self.loc_) + ",\n"
        returnstring += spaces*" " + "\"range_\":" + json.dumps(self.range_) + ",\n" 
        return returnstring


@dataclass(frozen=True)
class Program(Node):
    """
    Program Node class
        Inherits from Node class
    ...

    Attributes
    ----------
    body_ : List['Node']
        A list of nodes containing the body of the program. These can be any kind of nodes

    Methods
    -------
    jsonify(spaces=4)
        returns a json like string to print out the node into a json format.
    """
    body_: List['Node']
    
    def jsonify(self, spaces=0):
        returnstring = "{\"" + self.__class__.__name__ + "\":{\n"
        returnstring += super().jsonify(spaces=spaces+4)
        returnstring += (spaces+4)*" " + "\"body_\":{"+"\n"
        for i in range(len(self.body_)):
            returnstring += (spaces+8)*" " 
            returnstring += self.body_[i].jsonify(spaces=spaces+8)
            if i != len(self.body_)-1:
                returnstring += ","
            returnstring += "\n"
        returnstring += (spaces+4)*" " + "}\n"
        returnstring += spaces*" " + "}}\n"
        return returnstring


@dataclass(frozen=True)
class Identifier(Node):
    """
    Identifier Node class
        Inherits from Node class
    ...

    Attributes
    ----------
    name_ : str
        Name of the Identifier

    Methods
    -------
    jsonify(spaces=4)
        returns a json like string to print out the node into a json format.
    """
    name_ : str
    
    def jsonify(self, spaces=0):
        returnstring = "\"" + self.__class__.__name__ + "\":{\n"
        returnstring += super().jsonify(spaces=spaces+4)
        returnstring += (spaces+4)*" " + "\"name_\":\"" + str(self.name_) + "\"\n"
        returnstring += spaces*" " + "}"
        return returnstring


@dataclass(frozen=True)
class BlockStatement(Node):
    """
    Blockstatement Node class
        Inherits from Node class
    ...

    Attributes
    ----------
    body_ : List['Node]
        A list of nodes of which the blockstatement consists of.

    Methods
    -------
    jsonify(spaces=4)
        returns a json like string to print out the node into a json format.
    """
    body_: List['Node']
    
    def jsonify(self, spaces=0):
        returnstring = "\"" + self.__class__.__name__ + "\":{\n"
        returnstring += super().jsonify(spaces=spaces+4)
        returnstring += (spaces+4)*" " + "\"body_\":{" + "\n"
        for i in range(len(self.body_)):
            returnstring += (spaces+8)*" " 
            returnstring += self.body_[i].jsonify(spaces=spaces+8)
            if i != len(self.body_)-1:
                returnstring += ","
            returnstring += "\n"
        returnstring += (spaces+4)*" " + "}\n"
        returnstring += spaces*" " + "}"
        return returnstring


@dataclass(frozen=True)
class FunctionDeclaration(Node):
    """
    FunctionDeclaration Node class
        Inherits from Node class
    ...

    Attributes
    ----------
    id_ : Identifier
        An identifier node which holds the name (Identifier) of the function
    params_: List[Identifier]
        A list of identifiers that make up the function parameters
    body_ : Blockstatement
        A Blockstatement node which contains the body of the function

    Methods
    -------
    jsonify(spaces=4)
        returns a json like string to print out the node into a json format.
    """
    
    id_: Identifier
    params_: List[Identifier]
    body_: BlockStatement
    
    def jsonify(self, spaces=0):
        returnstring = "\"" + self.__class__.__name__ + "\":{\n"
        returnstring += super().jsonify(spaces=spaces+4)
        returnstring += (spaces+4)*" " + "\"id_\":\"" + str(self.id_) + "\",\n"
        returnstring += (spaces+4)*" " + "\"params_\":{" + "\n"
        for i in range(len(self.params_)):
            returnstring += (spaces+8)*" " 
            returnstring += self.params_[i].jsonify(spaces=spaces+8)
            if i != len(self.params_)-1:
                returnstring += ","
            returnstring += "\n"
        returnstring += (spaces+4)*" " + "},\n"
        returnstring += (spaces+4)*" " + "\"body_\":{\n"
        returnstring += (spaces+8)*" " + self.body_.jsonify(spaces=spaces+8) + "\n"
        returnstring += (spaces+4)*" " + "}\n"
        returnstring += spaces*" " + "}"
        return returnstring    


@dataclass(frozen=True)
class Literal(Node):
    """
    Literal Node class
        Inherits from Node class
    ...

    Attributes
    ----------
    value_ : Any
        The value of the literal
    raw_: Any
        The raw value of the literal

    Methods
    -------
    jsonify(spaces=4)
        returns a json like string to print out the node into a json format.
    """
    value_: Any
    raw_: str
    
    def jsonify(self, spaces=0):
        returnstring = "\"" + self.__class__.__name__ + "\":{\n"
        returnstring += super().jsonify(spaces=spaces+4)
        returnstring += (spaces+4)*" " + "\"value_\":" + str(self.value_) + ",\n"
        returnstring += (spaces+4)*" " + "\"raw_\":" + str(self.raw_) + "\n"
        returnstring += spaces*" " + "}"
        return returnstring
    

@dataclass(frozen=True)
class IfStatement(Node):
    """
    IfStatement Node class
        Inherits from Node class
    ...

    Attributes
    ----------
    test_ : Node
        A node containing a test for the if statement. Can be of type Literal, Identifier or BinaryExpression 
    consequent_: Blockstatement
        A Blockstatement containing the code which to execute if the if statement is resolves to True
    alternate_: Optional[Union['IfStatement', BlockStatement]]
        A Blockstatement, another if statement or nothing. This will be executed if the ifstatement resolves to False

    Methods
    -------
    jsonify(spaces=4)
        returns a json like string to print out the node into a json format.
    """
    test_: Node
    consequent_: BlockStatement
    alternate_: Optional[Union['IfStatement', BlockStatement]]

    def jsonify(self, spaces=0):
        returnstring = "\"" + self.__class__.__name__ + "\":{\n"
        returnstring += super().jsonify(spaces=spaces+4)
        returnstring += (spaces+4)*" " + "\"test_\":{\n"
        returnstring += (spaces+8)*" " + self.test_.jsonify(spaces=spaces+8) + "\n"
        returnstring += (spaces+4)*" " + "},\n"
        returnstring += (spaces+4)*" " + "\"consequent_\":{\n" 
        returnstring += (spaces+8)*" " + self.consequent_.jsonify(spaces=spaces+8) + "\n"
        returnstring += (spaces+4)*" " + "},\n" 
        returnstring += (spaces+4)*" " + "\"alternate_\":{\n" 
        returnstring += (spaces+8)*" " + (self.alternate_.jsonify(spaces=spaces+8) + "\n" if self.alternate_ else "\n")
        returnstring += (spaces+4)*" " + "}\n"
        returnstring += spaces*" " + "}"
        return returnstring


@dataclass(frozen=True)
class ReturnStatement(Node):
    """
    ReturnStatement Node class
        Inherits from Node class
    ...

    Attributes
    ----------
    argument_ : Node
        A node containing code to execute on if a return call is made

    Methods
    -------
    jsonify(spaces=4)
        returns a json like string to print out the node into a json format.
    """
    argument_: Node

    def jsonify(self, spaces=0):
        returnstring = "\"" + self.__class__.__name__ + "\":{\n"
        returnstring += super().jsonify(spaces=spaces+4)
        returnstring += (spaces+4)*" " + "\"argument_\":{\n" 
        returnstring += (spaces+8)*" " + self.argument_.jsonify(spaces=spaces+8) + "\n"
        returnstring += (spaces+4)*" " + "}\n" 
        returnstring += spaces*" " + "}"
        return returnstring


@dataclass(frozen=True)
class ExpressionStatement(Node):
    """
    ExpressionStatement Node class
        Inherits from Node class
    ...

    Attributes
    ----------
    expression_ : Node
        A node containing code to execute on if an Expression is parsed

    Methods
    -------
    jsonify(spaces=4)
        returns a json like string to print out the node into a json format.
    """
    expression_: Node
    
    def jsonify(self, spaces=0):
        returnstring = "\"" + self.__class__.__name__ + "\":{\n"
        returnstring += super().jsonify(spaces=spaces+4)
        returnstring += (spaces+4)*" " + "\"expression_\":" + self.expression_.jsonify(spaces=spaces+4) + "\n"
        returnstring += spaces*" " + "}"
        return returnstring


@dataclass(frozen=True)
class CallExpression(Node):
    """
    CallExpression Node class
        Inherits from Node class
    ...

    Attributes
    ----------
    arguments_ : List[Node]
        A list of nodes which indicate the argument a function is called with
    callee_: Identifier
        An Identifier node which holds information about which function is being called

    Methods
    -------
    jsonify(spaces=4)
        returns a json like string to print out the node into a json format.
    """
    arguments_: List[Node]
    callee_ : Identifier
    
    def jsonify(self, spaces=0):
        returnstring = "\"" + self.__class__.__name__ + "\":{\n"
        returnstring += super().jsonify(spaces=spaces+4)
        returnstring += (spaces+4)*" " + "\"arguments_\":{" + "\n"
        for i in range(len(self.arguments_)):
            returnstring += (spaces+8)*" " 
            returnstring += self.arguments_[i].jsonify(spaces=spaces+8)
            if i != len(self.arguments_)-1:
                returnstring += ","
            returnstring += "\n"
        returnstring += (spaces+4)*" " + "},\n"
        returnstring += (spaces+4)*" " + "\"callee_\":{\n" 
        returnstring += (spaces+8)*" " + self.callee_.jsonify(spaces=spaces+8) + "\n"
        returnstring += (spaces+4)*" " + "}\n"
        returnstring += spaces*" " + "}"
        return returnstring


@dataclass(frozen=True)
class UnaryExpression(Node):
    """
    UnaryExpression Node class
        Inherits from Node class
    ...

    Attributes
    ----------
    operator_ : str
        Operator for the unary expression
    argument_: Literal
        Argument for the unary expression

    Methods
    -------
    jsonify(spaces=4)
        returns a json like string to print out the node into a json format.
    """
    operator_: str
    argument_: Literal

    def jsonify(self, spaces=0):
        returnstring = "\"" + self.__class__.__name__ + "\":{\n"
        returnstring += super().jsonify(spaces=spaces+4)
        returnstring += (spaces+4)*" " + "\"operator_\":\"" + str(self.operator_) + "\",\n"
        returnstring += (spaces+4)*" " + "\"argument_\": {\n"
        returnstring += (spaces+8)*" " + self.argument_.jsonify(spaces=spaces+8) + "\n"
        returnstring += (spaces+4)*" " +"}\n"
        returnstring += spaces*" " + "}"
        return returnstring


@dataclass(frozen=True)
class VariableDeclaration(Node):
    """
    VariableDeclaration Node class
        Inherits from Node class
    ...

    Attributes
    ----------
    id_ : str
        Id for the variable that is declarated
    init_: Node
        Node indicating the how the variable must be initialised

    Methods
    -------
    jsonify(spaces=4)
        returns a json like string to print out the node into a json format.
    """
    id_: str
    init_: Node
    
    def jsonify(self, spaces=0):
        returnstring = "\"" + self.__class__.__name__ + "\":{\n"
        returnstring += super().jsonify(spaces=spaces+4)
        returnstring += (spaces+4)*" " + "\"id_\":\"" + str(self.id_) + "\",\n"
        returnstring += (spaces+4)*" " + "\"init_\": {\n"
        returnstring += (spaces+8)*" " + self.init_.jsonify(spaces=spaces+8) + "\n"
        returnstring += (spaces+4)*" " +"}\n"
        returnstring += spaces*" " + "}"
        return returnstring


@dataclass(frozen=True)
class BinaryExpression(Node):
    """
    BinaryExpression Node class
        Inherits from Node class
    ...

    Attributes
    ----------
    operator_ : str
        Operator for the binary expression
    left_: Node
        Left node for the binary expression
    right_: Node
        Right node for the binary expression

    Methods
    -------
    jsonify(spaces=4)
        returns a json like string to print out the node into a json format.
    """
    operator_ : str
    left_: Node
    right_: Node
    
    def jsonify(self, spaces=0):
        returnstring = "\"" + self.__class__.__name__ + "\":{\n"
        returnstring += super().jsonify(spaces=spaces+4)
        returnstring += (spaces+4)*" " + "\"operator_\":\"" + str(self.operator_) + "\",\n"
        returnstring += (spaces+4)*" " + "\"left_\":{\n"
        returnstring += (spaces+8)*" " + self.left_.jsonify(spaces=spaces+8) + "\n"
        returnstring += (spaces+4)*" " +"},\n"
        returnstring += (spaces+4)*" " + "\"right_\":{\n"
        returnstring += (spaces+8)*" " + self.right_.jsonify(spaces=spaces+8) + "\n"
        returnstring += (spaces+4)*" " +"}\n"
        returnstring += spaces*" " + "}"
        return returnstring