import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append('../../')

import lexer
from token_types import TokenExpressions, TokenTypes

class TestParser(unittest.TestCase):
    pass

if __name__== "__main__":
    unittest.main(verbosity=2)