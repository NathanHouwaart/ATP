import unittest
import sys
import os
import inspect

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append("C:/Users/Nathan/Documents/ATP/parser_")

from lexer.lexer import lex, search_match
from parser_.parser_ import parse
from misc.token_types import *
from misc.node_types import Program

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
code_samples_dir = root_dir + "/tests/code_samples/valid/"
code_samples_dir_invalid = root_dir + "/tests/code_samples/invalid/"

class TestParser(unittest.TestCase):
    
    def open_lex_parse_compare(self, file_path):
        with open(file_path, 'rb') as f:
            code = f.read().decode("utf-8")

        tokens = lex(code, search_match, TokenExpressions)
        tokens = list(filter(lambda token: token.tokentype_ != TokenTypes.NONE, tokens))
        
        parsed, leftover_token = parse(code, tokens)
        program = Program(loc_={'start': {'line': 1, 'index': 0}, "end":{"line":tokens[-1].loc_["start"]["line"], "index":tokens[-1].loc_["start"]["index"]}}, range_=[0, len(code)], body_=parsed)

        filename, _        = os.path.splitext(os.path.basename(file_path))
        folder_output      = root_dir + "/tests/parser_tests/test_output/" + os.path.basename(os.path.dirname(file_path))
        folder_required    = root_dir + "/tests/parser_tests/required/" + os.path.basename(os.path.dirname(file_path))
        output_file        = folder_output + "/" + filename + ".json"
        required_file      = folder_required + "/" + filename + ".json"
        
        if not os.path.exists(folder_output): os.makedirs(folder_output)
        
        with open(output_file, "w") as f:
            f.write(program.pretty_print())
        self.compare_files(required_file, output_file)

  
    def compare_files(self, required, test):
        with open(required, "r") as f:
            required_output = f.read()
        
        with open(test, "r") as f:
            test_output = f.read()
        self.assertEqual(required_output, test_output)
    
    
    def test_unary_expressions(self):
        self.open_lex_parse_compare(code_samples_dir + "unary_expression/unary_expression_identifier.txt")
        self.open_lex_parse_compare(code_samples_dir + "unary_expression/unary_expression_int.txt")
        self.open_lex_parse_compare(code_samples_dir + "unary_expression/unary_expression_call_statement.txt")
        
    def test_invalid_unary_expressions(self):
        try: self.open_lex_parse_compare(code_samples_dir_invalid + "unary_expression/no_expression_minus.txt")
        except Exception as e:     
            self.assertIn("Expected expression, literal, or function call\nFile <placeholder>, line 1\n\t📁 var1 = -\n\t          ^^^", str(e))
        
        try: self.open_lex_parse_compare(code_samples_dir_invalid + "unary_expression/no_expression_plus.txt")
        except Exception as e:     
            self.assertIn("Expected expression, literal, or function call\nFile <placeholder>, line 1\n\t📁 var1 = +\n\t          ^^^", str(e))
            return
        self.fail()
    
    def test_invalid_call_expression(self):
        try: self.open_lex_parse_compare(code_samples_dir_invalid + "call_expression/call_invalid_separator.txt")
        except Exception as e:
            self.assertIn("Missing '|' between multiple parameters\nFile <placeholder>, line 1\n\t✆ fib param1 param2 ✆\n\t             ^^^^^^", str(e))
        
        try: self.open_lex_parse_compare(code_samples_dir_invalid + "call_expression/call_no_end.txt")
        except Exception as e:
            self.assertIn("Expected identifier after call statement\nFile <placeholder>, line 1\n\t✆ fib param1 | ✆\n\t                ^^^", str(e))
            return
        self.fail()
        
    def test_simple_expressions(self):
        self.open_lex_parse_compare(code_samples_dir + "simple_expression/simple_divide_expression.txt")
        self.open_lex_parse_compare(code_samples_dir + "simple_expression/simple_minus_expression.txt")
        self.open_lex_parse_compare(code_samples_dir + "simple_expression/simple_multiply_expression.txt")
        self.open_lex_parse_compare(code_samples_dir + "simple_expression/simple_plus_expression.txt")
        self.open_lex_parse_compare(code_samples_dir + "simple_expression/call_expression_multiple_param.txt")
        self.open_lex_parse_compare(code_samples_dir + "simple_expression/call_expression_no_param.txt")
        self.open_lex_parse_compare(code_samples_dir + "simple_expression/call_expression_one_param.txt")
        
    def test_chained_expression(self):
        self.open_lex_parse_compare(code_samples_dir + "chained_expression/multiply_divide_expression.txt")
        self.open_lex_parse_compare(code_samples_dir + "chained_expression/plus_minus_expression.txt")
        self.open_lex_parse_compare(code_samples_dir + "chained_expression/plus_minus_divide_multiply_expression.txt")
        self.open_lex_parse_compare(code_samples_dir + "chained_expression/plus_minus_divide_multiply_parentheseis_expression.txt")
        self.open_lex_parse_compare(code_samples_dir + "chained_expression/plus_minus_divide_multiply_call_expression.txt")
        self.open_lex_parse_compare(code_samples_dir + "chained_expression/plus_minus_divide_multiply_call_parenthesies_expression_.txt")
    
    def test_call_expression(self):
        self.open_lex_parse_compare(code_samples_dir + "call_expression/call_no_params.txt")
        self.open_lex_parse_compare(code_samples_dir + "call_expression/call_one_param.txt")
        self.open_lex_parse_compare(code_samples_dir + "call_expression/call_multiple_params.txt")
        self.open_lex_parse_compare(code_samples_dir + "call_expression/call_in_call_expressiont.txt")
        
    def test_function_declaration(self):
        self.open_lex_parse_compare(code_samples_dir + "function_declarations/function_no_param.txt")
        self.open_lex_parse_compare(code_samples_dir + "function_declarations/function_one_param.txt")
        self.open_lex_parse_compare(code_samples_dir + "function_declarations/function_multiple_param.txt")

    def test_if_statement(self):
        self.open_lex_parse_compare(code_samples_dir + "if_statements\if_elif_elif_else_statement.txt")
        self.open_lex_parse_compare(code_samples_dir + "if_statements\if_elif_else_statement.txt")
        self.open_lex_parse_compare(code_samples_dir + "if_statements\if_else_tatement.txt")
        self.open_lex_parse_compare(code_samples_dir + "if_statements\if_statement.txt")
        self.open_lex_parse_compare(code_samples_dir + "if_statements\if_statement_two_expressions_and.txt")
        self.open_lex_parse_compare(code_samples_dir + "if_statements\if_statement_two_expressions_or.txt")
        self.open_lex_parse_compare(code_samples_dir + "if_statements\if_statement_function_call.txt")
        
    def test_invalid_if_statement(self):
        try: self.open_lex_parse_compare(code_samples_dir_invalid + "if_statements\if_statement_no_end.txt")
        except Exception as e:
            self.assertIn("Expected '¿', '⁈', or '⁇' after if statement\nFile <placeholder>, line 2\n\t    📁 var1 = 1\n\t              ^^^", str(e))

        try: self.open_lex_parse_compare(code_samples_dir_invalid + "if_statements\if_else_statement_no_end.txt")
        except Exception as e:
            self.assertIn("Expected '¿' after if statement end\nFile <placeholder>, line 4\n\t    📁 var1 = 10\n\t               ^^^", str(e))
        
        try: self.open_lex_parse_compare(code_samples_dir_invalid + "if_statements\if_elif_else_statement_no_end.txt")
        except Exception as e:
            self.assertIn("Expected '¿' after if statement end\nFile <placeholder>, line 6\n\t    📁 var1 = 10\n\t               ^^^", str(e))
            
        try: self.open_lex_parse_compare(code_samples_dir_invalid + "if_statements\if_elif_elif_else_statement_no_end.txt")
        except Exception as e:
            self.assertIn("Expected '¿' after if statement end\nFile <placeholder>, line 8\n\t    📁 var1 = 10\n\t               ^^^", str(e))
        
        try: self.open_lex_parse_compare(code_samples_dir_invalid + "if_statements\else_statement_without_if.txt")
        except Exception as e:
            self.assertIn("Invalid Syntax\nFile <placeholder>, line 1\n\t⁇ ––>\r\n\t^", str(e))
        
        try: self.open_lex_parse_compare(code_samples_dir_invalid + "if_statements\elif_statement_without_if.txt")
        except Exception as e:
            self.assertIn("Invalid Syntax\nFile <placeholder>, line 1\n\t⁈ var1 == 3 ––>\r\n\t^", str(e))
            return
        self.fail()
    
    def test_invalid_chained_expression(self):
        try: self.open_lex_parse_compare(code_samples_dir_invalid + "chained_expression\missing_left_parenthesies.txt")
        except Exception as e:
            self.assertIn("Invalid Syntax\nFile <placeholder>, line 1\n\t📁 test = 10 * 2 + 4>\n\t                   ^", str(e))
            
        try: self.open_lex_parse_compare(code_samples_dir_invalid + "chained_expression\missing_right_parenthesies.txt")
        except Exception as e:
            self.assertIn("Missing right parenthesies\nFile <placeholder>, line 1\n\t📁 test = 10 * <2 + 4\n\t                    ^^^", str(e))
            return
        self.fail()
        
    def test_invalid_simple_expression(self):
        try: self.open_lex_parse_compare(code_samples_dir_invalid + "simple_expression\invalid_divide_expression.txt")
        except Exception as e:
            self.assertIn("xpected expression, literal, or function call\nFile <placeholder>, line 1\n\t📁 test = 1 // 2\n\t            ^", str(e))
            
        try: self.open_lex_parse_compare(code_samples_dir_invalid + "simple_expression\invalid_minus_expression.txt")
        except Exception as e:
            self.assertIn("Expected expression, literal, or function call\nFile <placeholder>, line 1\n\t📁 test = 1 -* 2\n\t            ^", str(e))
        
        try: self.open_lex_parse_compare(code_samples_dir_invalid + "simple_expression\invalid_multiply_expression.txt")
        except Exception as e:
            self.assertIn("Expected expression, literal, or function call\nFile <placeholder>, line 1\n\t📁 test = 1 */ 2\n\t            ^", str(e))
        
        try: self.open_lex_parse_compare(code_samples_dir_invalid + "simple_expression\invalid_plus_expression.txt")
        except Exception as e:
            self.assertIn("Expected expression, literal, or function call\nFile <placeholder>, line 1\n\t📁 test = 1 +*2\n\t            ^", str(e))
            return
        self.fail()
        
    def test_invalid_function_declaration(self):
        try: self.open_lex_parse_compare(code_samples_dir_invalid + "function_declarations\\function_declaration_empty_body.txt")
        except Exception as e:
            self.assertIn("Function body cannot be empty\nFile <placeholder>, line 1\n\tƒ test | α var1 | α var2 ––>\r\n\t  ^^^^", str(e))
            
        try: self.open_lex_parse_compare(code_samples_dir_invalid + "function_declarations\\function_declaration_invalid_parameters.txt")
        except Exception as e:
            self.assertIn("Expected '|' or '––>' after function parameter declaration\nFile <placeholder>, line 1\n\tƒ test α var1 α var2 ––>\r\n\t       ^", str(e))
        
        try: self.open_lex_parse_compare(code_samples_dir_invalid + "function_declarations\\function_declaration_invalid_return.txt")
        except Exception as e:
            self.assertIn("Expected closing '⮐' after return statement\nFile <placeholder>, line 2\n\t    ⮐ var1 + var2\r\n\t                 ^^", str(e))
        
        try: self.open_lex_parse_compare(code_samples_dir_invalid + "function_declarations\\function_declaration_no_indation_sign.txt")
        except Exception as e:
            self.assertIn("Expected '––>' after function declaration\nFile <placeholder>, line 1\n\tƒ test | α var1 | α var2\r\n\t                        ^^", str(e))
            return
        self.fail()

    
if __name__== "__main__":
    
    # test = TestParser()
    # test.test_unary_expression()
    
    unittest.main(verbosity=2)
    