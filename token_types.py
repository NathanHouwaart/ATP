from enum import Enum
import re
from typing import *

class TokenTypes(Enum):
    NONE = 0
    FUNCTION_DECLARATION = 1
    INDENTATION = 2
    VARIABLE_DECLARATION = 3
    LINE_NO = 4
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

TokenExpressions = [
    (r"[\r]?[\n]",                  TokenTypes.NEW_LINE),
    (r"[ \t]+",                     TokenTypes.NONE),
    (r"#[^\n]*",                    TokenTypes.NONE),
    (r"\bƒ\b",                      TokenTypes.FUNCTION_DECLARATION),
    (r"––>\B",                      TokenTypes.INDENTATION),
    (r"\bα\b",                      TokenTypes.VARIABLE_DECLARATION),
    (r"([0-9]+\.[ ]+)",             TokenTypes.LINE_NO),
    (r"(\==)",                      TokenTypes.IS_EQUAL),
    (r"=",                          TokenTypes.IS),
    (r"(\+)",                       TokenTypes.PLUS),
    (r"(\-)",                       TokenTypes.MINUS),
    (r"(\/)",                       TokenTypes.DIVIDE),
    (r"(\*)",                       TokenTypes.MULTIPLY),
    (r"(\|)",                       TokenTypes.SEPARATOR),
    (r"(\>)",                       TokenTypes.RIGHT_PARENTHESIES),
    (r"(\<)",                       TokenTypes.LEFT_PARENTHESIES),
    (r"(\B\?\B)",                   TokenTypes.IF),
    (r"(\B¿¿\B)",                   TokenTypes.ELSE_IF),
    (r"(\B¿\B)",                    TokenTypes.ELSE),
    (r"(\B\🖨\B)",                  TokenTypes.PRINT),
    (r"(\B\📞\B)",                  TokenTypes.CALL),
    (r"(\B\⚡\B)",                  TokenTypes.POWER),
    (r"(\bexit\b)",                 TokenTypes.RETURN),
    (r'[0-9]+\b',                   TokenTypes.INT),
    (r'[A-Za-z][A-Za-z0-9_]*\b',    TokenTypes.IDENTIFIER),
]