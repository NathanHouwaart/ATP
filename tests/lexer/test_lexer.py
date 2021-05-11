import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer.lexer import lex, search_match
from misc.token_types import *

code_samples = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestLexer(unittest.TestCase):

        
    def lex_and_compare_required_vs_output(self, file_path, required_token_order):
        with open(file_path, 'rb') as f:
            code = f.read().decode("utf-8")

        tokens = lex(code, search_match, TokenExpressions)
        tokens = list(filter(lambda token: token.tokentype_ != TokenTypes.NONE, tokens))
        
        for i in range(len(required_token_order)):
            self.assertEqual(tokens[i].tokentype_, required_token_order[i], msg=file_path)


    def test_recognise_all_tokens_with_spaces(self):
        token_order = [ 
            TokenTypes.TAB, TokenTypes.NEW_LINE, TokenTypes.FUNCTION_DECLARATION, TokenTypes.INDENTATION,
            TokenTypes.FUNCTION_DECLARATION_END, TokenTypes.VARIABLE_DECLARATION, TokenTypes.PARAMETER, 
            TokenTypes.IS, TokenTypes.IS_EQUAL, TokenTypes.PLUS, TokenTypes.MINUS, TokenTypes.DIVIDE, 
            TokenTypes.OR, TokenTypes.AND, TokenTypes.MULTIPLY, TokenTypes.SEPARATOR, TokenTypes.RIGHT_PARENTHESIES, 
            TokenTypes.LEFT_PARENTHESIES, TokenTypes.GREATER_THAN, TokenTypes.SMALLER_THAN, TokenTypes.IF, 
            TokenTypes.ELSE_IF, TokenTypes.ELSE, TokenTypes.IF_STATEMENT_END, TokenTypes.PRINT, TokenTypes.CALL, 
            TokenTypes.RETURN, TokenTypes.INT, TokenTypes.IDENTIFIER
        ]
        self.lex_and_compare_required_vs_output(code_samples +"/code_samples/valid/all_tokens_with_spaces.txt", token_order)


    def test_recognise_all_token_without_spaces(self):
        token_order = [ 
            TokenTypes.FUNCTION_DECLARATION, TokenTypes.INDENTATION,TokenTypes.FUNCTION_DECLARATION_END, 
            TokenTypes.VARIABLE_DECLARATION, TokenTypes.TAB, TokenTypes.NEW_LINE, TokenTypes.PARAMETER, 
            TokenTypes.IS_EQUAL, TokenTypes.IS, TokenTypes.PLUS, TokenTypes.MINUS, TokenTypes.DIVIDE, 
            TokenTypes.OR, TokenTypes.AND, TokenTypes.MULTIPLY, TokenTypes.SEPARATOR, TokenTypes.RIGHT_PARENTHESIES, 
            TokenTypes.LEFT_PARENTHESIES, TokenTypes.GREATER_THAN, TokenTypes.SMALLER_THAN, TokenTypes.IF, 
            TokenTypes.ELSE_IF, TokenTypes.ELSE, TokenTypes.IF_STATEMENT_END, TokenTypes.PRINT, TokenTypes.CALL, 
            TokenTypes.RETURN, TokenTypes.INT, TokenTypes.IDENTIFIER
        ]
        self.lex_and_compare_required_vs_output(code_samples +"/code_samples/valid/all_tokens_without_spaces.txt", token_order)


    def test_expression(self):
        token_order_simple_expression = [
            TokenTypes.VARIABLE_DECLARATION, TokenTypes.IDENTIFIER, TokenTypes.IS, 
            TokenTypes.INT, TokenTypes.PLUS, TokenTypes.INT
        ]
        token_order_big_expression = [
            TokenTypes.VARIABLE_DECLARATION, TokenTypes.IDENTIFIER, TokenTypes.IS, TokenTypes.LEFT_PARENTHESIES,
            TokenTypes.IDENTIFIER, TokenTypes.MINUS, TokenTypes.INT, TokenTypes.RIGHT_PARENTHESIES, TokenTypes.MULTIPLY,
            TokenTypes.LEFT_PARENTHESIES, TokenTypes.INT, TokenTypes.MINUS, TokenTypes.INT, TokenTypes.RIGHT_PARENTHESIES
        ]
        
        self.lex_and_compare_required_vs_output(code_samples + "/code_samples/valid/simple_expression.txt", token_order_simple_expression)
        self.lex_and_compare_required_vs_output(code_samples + "/code_samples/valid/big_expression.txt", token_order_big_expression)


    def test_function_declaration(self):
        token_order_function_declaratrion_without_parameters = [
            TokenTypes.FUNCTION_DECLARATION, TokenTypes.IDENTIFIER, TokenTypes.INDENTATION, 
            TokenTypes.NEW_LINE, TokenTypes.FUNCTION_DECLARATION_END
        ]
        token_order_function_declaratrion_with_parameters = [
            TokenTypes.FUNCTION_DECLARATION, TokenTypes.IDENTIFIER, TokenTypes.SEPARATOR,
            TokenTypes.PARAMETER,TokenTypes.IDENTIFIER, TokenTypes.SEPARATOR, 
            TokenTypes.PARAMETER, TokenTypes.IDENTIFIER, TokenTypes.INDENTATION, 
            TokenTypes.NEW_LINE, TokenTypes.FUNCTION_DECLARATION_END
        ]
        token_order_function_with_body = [
            TokenTypes.FUNCTION_DECLARATION, TokenTypes.IDENTIFIER, TokenTypes.SEPARATOR,
            TokenTypes.PARAMETER, TokenTypes.IDENTIFIER, TokenTypes.INDENTATION, 
            TokenTypes.NEW_LINE, TokenTypes.TAB, TokenTypes.RETURN, TokenTypes.INT, TokenTypes.PLUS,
            TokenTypes.IDENTIFIER, TokenTypes.NEW_LINE, TokenTypes.FUNCTION_DECLARATION_END
        ]

        self.lex_and_compare_required_vs_output(code_samples + "/code_samples/valid/function_declaration_without_parameters.txt", token_order_function_declaratrion_without_parameters)
        self.lex_and_compare_required_vs_output(code_samples + "/code_samples/valid/function_declaration_with_parameters.txt", token_order_function_declaratrion_with_parameters)
        self.lex_and_compare_required_vs_output(code_samples + "/code_samples/valid/function_declaration_with_body.txt", token_order_function_with_body)


    def test_if_statement(self):
        token_order_if_statement = [
            TokenTypes.IF, TokenTypes.IDENTIFIER, TokenTypes.SMALLER_THAN, TokenTypes.INT, TokenTypes.INDENTATION,
            TokenTypes.NEW_LINE, TokenTypes.TAB, TokenTypes.VARIABLE_DECLARATION, TokenTypes.IDENTIFIER, 
            TokenTypes.IS, TokenTypes.INT, TokenTypes.IF_STATEMENT_END, TokenTypes.NEW_LINE, TokenTypes.ELSE_IF, 
            TokenTypes.IDENTIFIER, TokenTypes.IS_EQUAL, TokenTypes.INT, TokenTypes.INDENTATION, TokenTypes.NEW_LINE, 
            TokenTypes.TAB, TokenTypes.VARIABLE_DECLARATION, TokenTypes.IDENTIFIER, TokenTypes.IS, TokenTypes.INT, 
            TokenTypes.IF_STATEMENT_END, TokenTypes.NEW_LINE, TokenTypes.ELSE, TokenTypes.INDENTATION, TokenTypes.NEW_LINE, 
            TokenTypes.TAB, TokenTypes.VARIABLE_DECLARATION, TokenTypes.IDENTIFIER, TokenTypes.IS, TokenTypes.INT, 
            TokenTypes.IF_STATEMENT_END
        ]
        self.lex_and_compare_required_vs_output(code_samples + "/code_samples/valid/if_statement.txt", token_order_if_statement)


    def test_function_call(self):
        token_order_function_call = [
            TokenTypes.VARIABLE_DECLARATION, TokenTypes.IDENTIFIER, TokenTypes.IS, TokenTypes.LEFT_PARENTHESIES,TokenTypes.CALL, 
            TokenTypes.IDENTIFIER, TokenTypes.INT, TokenTypes.CALL, TokenTypes.PLUS, TokenTypes.CALL, TokenTypes.IDENTIFIER, 
            TokenTypes.INT, TokenTypes.CALL, TokenTypes.RIGHT_PARENTHESIES
        ]
        self.lex_and_compare_required_vs_output(code_samples + "/code_samples/valid/function_call.txt", token_order_function_call)
        
    
    def test_invalid_variable_declaration(self):
        try: 
            self.lex_and_compare_required_vs_output(code_samples +"/code_samples/invalid/invalid_identifier.txt", None)
        except Exception as e:          
            self.assertIn("Invalid Syntax\nFile <placeholder>, line 1\n\t📁 02var1 = 12\n\t   ^^^^", str(e))
            return
        self.fail()
    
    
    def test_invalid_identifier(self):
        try: 
            self.lex_and_compare_required_vs_output(code_samples + "/code_samples/invalid/invalid_variable_declaration.txt", None)
        except Exception as e:
            self.assertIn("Invalid Syntax\nFile <placeholder>, line 1\n\t📁var1 =12\n\t ^^^^", str(e))
            return
        self.fail()

    
    def test_invalid_syntax(self):
        try:
            self.lex_and_compare_required_vs_output(code_samples + "/code_samples/invalid/unknown_syntax.txt", None)
        except Exception as e:
            self.assertIn("Invalid Syntax\nFile <placeholder>, line 1\n\t📁 var1=(1+2)\n\t        ^^^^", str(e))
            return
        self.fail()


if __name__== "__main__":
    # print()
    # exit()
    unittest.main(verbosity=2)