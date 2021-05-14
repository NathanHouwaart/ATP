from enum import Enum
from typing import Tuple, Callable, Optional, Dict, List, NamedTuple, Any
import re

class Token(NamedTuple):
    loc_: Dict[str, Dict[str,int]]
    range_: List[int]
    value_: str
    tokentype_: 'TokenTypes'


class TokenTypes(Enum):
    NONE = 0
    FUNCTION_DECLARATION = 1
    INDENTATION = 2
    VARIABLE_DECLARATION = 3
    CODE_LINE = 4
    IS = 5
    PLUS = 6
    MINUS = 7
    DIVIDE = 8
    MULTIPLY = 9
    SEPARATOR = 10
    LEFT_PARENTHESIES = 11
    RIGHT_PARENTHESIES = 12
    IS_EQUAL = 13
    IF = 14
    ELSE_IF = 15
    ELSE = 16
    PRINT = 17
    CALL = 18
    RETURN = 19
    TAB = 20
    INT = 21
    FLOAT = 22
    IDENTIFIER =23
    EOF = 24
    POWER = 25
    SPACE = 26
    NEW_LINE = 27
    GREATER_THAN = 28
    SMALLER_THAN = 29
    FUNCTION_LINE = 30
    PARAMETER = 31
    OR = 32
    AND = 33
    IF_STATEMENT_END = 34
    FUNCTION_DECLARATION_END = 35

TokenExpressions = [
    (r"[\r]?[\n]",                  TokenTypes.NEW_LINE),
    (r"([ ][ ][ ][ ])",             TokenTypes.TAB),
    (r"[ ]+",                       TokenTypes.NONE),
    (r"#[^\n]*",                    TokenTypes.NONE),
    (r"\bƒ\b",                      TokenTypes.FUNCTION_DECLARATION),
    (r"––>\B",                      TokenTypes.INDENTATION),
    (r"\B––\B",                     TokenTypes.FUNCTION_DECLARATION_END),
    (r"\B📁\B",                     TokenTypes.VARIABLE_DECLARATION),
    (r"\bα\b",                      TokenTypes.PARAMETER),
    (r"(\==)",                      TokenTypes.IS_EQUAL),
    (r"=",                          TokenTypes.IS),
    (r"(\+)",                       TokenTypes.PLUS),
    (r"(\-)",                       TokenTypes.MINUS),
    (r"(\/)",                       TokenTypes.DIVIDE),
    (r"(\∨)",                       TokenTypes.OR),
    (r"(\∧)",                       TokenTypes.AND),
    (r"(\*)",                       TokenTypes.MULTIPLY),
    (r"(\|)",                       TokenTypes.SEPARATOR),
    (r"(\>)",                       TokenTypes.RIGHT_PARENTHESIES),
    (r"(\<)",                       TokenTypes.LEFT_PARENTHESIES),
    (r"\B\▲\B",                     TokenTypes.GREATER_THAN),
    (r"\B\▼\B",                     TokenTypes.SMALLER_THAN),
    (r"(\B\?\B)",                   TokenTypes.IF),
    (r"(\B⁈\B)",                    TokenTypes.ELSE_IF),
    (r"(\B⁇\B)",                    TokenTypes.ELSE),
    (r"(\B¿\B)",                    TokenTypes.IF_STATEMENT_END),
    (r"(\B\🖨\B)",                  TokenTypes.PRINT),
    (r"(\B\✆\B)",                   TokenTypes.CALL),
    (r"(\B\⚡\B)",                  TokenTypes.POWER),
    (r"(\B⮐\B)",                    TokenTypes.RETURN),
    (r'[0-9]+\b',                   TokenTypes.INT),
    (r'[A-Za-z][A-Za-z0-9_]*\b',    TokenTypes.IDENTIFIER),
]   