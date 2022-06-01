"""
@file main.py
@author Nathan Houwaart (nathan.houwaart@student.hu.nl)
@brief This file is used to lex, parse and interpret a file containing the alt-f4 programming language
@version 1.0
@date 16-05-2021
"""

import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from lexer_module.lexer import lex, search_match
from parser_module.parser import parse
from interpreter_module.interpreter import interpret
from misc.token_types import *
from misc.node_types import Program

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No source file provided")
        exit()

    with open(sys.argv[1], 'rb') as f:
        code = f.read().decode("utf-8")

    tokens = lex(code, search_match, TokenExpressions)
    tokens = list(filter(lambda token: token.tokentype_ != TokenTypes.NONE, tokens))

    parsed, leftover_token = parse(code, tokens)
    program = Program(loc_={'start': {'line': 1, 'index': 0}, "end":{"line":tokens[-1].loc_["start"]["line"], "index":tokens[-1].loc_["start"]["index"]}}, range_=[0, len(code)], body_=parsed)

    with open("pretty_printed.json", "wb") as f:
        f.write(program.jsonify().encode("utf-8"))
    
    time_start = time.time()
    result = interpret(code, program)
    time_stop = time.time()
    print("program finished in", round(time_stop-time_start, 5), "s")