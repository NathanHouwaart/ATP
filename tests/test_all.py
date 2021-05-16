"""
@file test_all.py
@author Nathan Houwaart (nathan.houwaart@student.hu.nl)
@brief This file bundels the lexer, parser and interpreter tests of the alt-f4 programming language
@version 1.0
@date 16-05-2021
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import lexer_tests.test_lexer as test_lexer
import parser_tests.test_parser as test_parser
import interpreter_tests.test_interpreter as test_interpreter
import unittest


if __name__ == "__main__":
    lexer       = unittest.TestLoader().loadTestsFromModule(test_lexer)
    parser      = unittest.TestLoader().loadTestsFromModule(test_parser)
    interpreter = unittest.TestLoader().loadTestsFromModule(test_interpreter)

    unittest.TextTestRunner(verbosity=2).run(lexer)
    unittest.TextTestRunner(verbosity=2).run(parser)
    unittest.TextTestRunner(verbosity=2).run(interpreter)