from typing import *
import operator
from token_s import Token
from token_types import *
from parser_node_types import *
import sys
import re
import itertools
import pprint

class Tree(NamedTuple):
    left : Union['Tree', int]
    right : Union['Tree', int]

A = TypeVar('A')
def search_match(characters: str, token_expressions: List[A], line_no=1, total_index=0) -> Optional[A]:
    if len(token_expressions) == 0:
        return None, None
    head, *tail = token_expressions
    pattern, tag = head
    
    regex = re.compile(pattern)
    match = regex.match(characters, total_index)
    return (match, tag) if match else search_match(characters, tail, line_no, total_index)


A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')
D = TypeVar('D')
def lex(characters: str, search_match_f: Callable[[A,B], Tuple[C, D]], token_expressions: List[B], line_no: int=1, index: int=0, total_index: int=0) -> Tuple[List[C], Optional[str]]:
    if len(characters) == total_index:
        token_loc={"start":{"line": line_no, "index":index}}
        token_range=[total_index,total_index+2]  
        return [Token(loc_=token_loc, range_=token_range, value_="\00", tokentype_=TokenTypes.EOF)]
    
    match, tokentype = search_match_f(characters, token_expressions, line_no, total_index)
    if not match: raise Exception(f"invalid syntax: {characters[total_index:].split()[0]}")

    text    = match.group(0)
    offset  = match.end(0) - match.start(0)

    token_loc={"start":{"line": line_no, "index":index}}
    token_range = [match.start(0), match.end(0)]

    token   = Token(loc_=token_loc, range_=token_range, value_=text, tokentype_=tokentype)

    if tokentype == TokenTypes.NEW_LINE: line_no +=1; index =0; offset = 0
    return [token] + lex(characters, search_match_f, token_expressions, line_no, index + offset, match.end(0))

def parse_number(tokens) -> Optional[None]:
    """factor : INTEGER | LPAREN expr RPAREN"""
    head, *tail = tokens
    if head.tokentype_ in (TokenTypes.PLUS, TokenTypes.MINUS):
        node, tail = parse_number(tail)
        return UnaryExpression(loc_={}, range_=[], operator_=head.tokentype_, argument_=node), tail
    if head.tokentype_ in (TokenTypes.INT, TokenTypes.FLOAT):
        return Literal(loc_={}, range_=[], value_=int(head.value_), raw_=head.value_), tail
    if head.tokentype_ == TokenTypes.IDENTIFIER:
        return Identifier(loc_={}, range_=[], name_=head.value_), tail
    if head.tokentype_ == TokenTypes.LEFT_PARENTHESIES:
        node, tokens = parse_expr(tail)
        head, *tail = tokens
        if head.tokentype_ != TokenTypes.RIGHT_PARENTHESIES:
            raise Exception("Missing right parenthesies")
        return node, tail
    
def parse_term(tokens):
    node, tokens = parse_number(tokens)
    node, tokens = loop(node, tokens, (TokenTypes.MULTIPLY, TokenTypes.DIVIDE))
    return node, tokens

def parse_expr(tokens):
    node, tokens = parse_term(tokens)
    node, tokens = loop(node, tokens, (TokenTypes.MINUS, TokenTypes.PLUS))
    return node, tokens


def loop(node, tokens, token_types):
    head, *tail = tokens
    if head.tokentype_ in token_types:
        token = head
        right, tokens = parse_term(tail)
        node = CallExpression(loc_={}, range_=[], type_=head.tokentype_, left_=node, right_=right)
        return loop(node, tokens, token_types)
    if head.tokentype_ == TokenTypes.NONE:
        return loop(node, tail, token_types)
    return node, tokens


def parse_variable_declaration(characters, tokens: List[A]):
    declaration_sign, identifier, *tail = tokens  
    if identifier.tokentype_ != TokenTypes.IDENTIFIER:
        line_no_error       = declaration_sign.loc_["start"]["line"]
        start_index_error   = declaration_sign.loc_["start"]["index"]
        invalid_chars       = characters.split("\n")[declaration_sign.loc_["start"]["line"]-1]
        raise Exception(f"Expected identifier after variable declaration\nFile <placeholder>, line {line_no_error}\n\t{invalid_chars}\n\t{' '*start_index_error+'^^^^'}")
    is_token, *tail = tail
    if is_token.tokentype_ != TokenTypes.IS:
        line_no_error       = is_token.loc_["start"]["line"]
        start_index_error   = is_token.loc_["start"]["index"]
        invalid_chars       = characters.split("\n")[is_token.loc_["start"]["line"]-1]
        raise Exception(f"Expected '='\nFile <placeholder>, line {line_no_error}\n\t{invalid_chars}\n\t{' '*start_index_error+'^^^^'}")
    value, *_ = tail
    if value.tokentype_ not in (TokenTypes.IDENTIFIER, TokenTypes.MINUS, TokenTypes.PLUS, TokenTypes.INT, TokenTypes.FLOAT, TokenTypes.LEFT_PARENTHESIES):
        line_no_error       = value.loc_["start"]["line"]
        start_index_error   = value.loc_["start"]["index"]
        invalid_chars       = characters.split("\n")[value.loc_["start"]["line"]-1]
        raise Exception(f"Expected expression after '=' statement\nFile <placeholder>, line {line_no_error}\n\t{invalid_chars}\n\t{' '*start_index_error+'^^^^'}")
    node, tokens = parse_expr(tail)
    node = VariableDeclaration(loc_={}, range_=[],id_=identifier.value_, init_=node)
    return node, tokens


def parse_function_declaration(characters:str, tokens: List[A]):
    declaration_sign, identifier, *tail = tokens
    if identifier.tokentype_ != TokenTypes.IDENTIFIER:
        line_no_error       = declaration_sign.loc_["start"]["line"]
        start_index_error   = declaration_sign.loc_["start"]["index"]
        invalid_chars       = characters.split("\n")[declaration_sign.loc_["start"]["line"]-1]
        raise Exception(f"Expected identifier after function declaration\nFile <placeholder>, line {line_no_error}\n\t{invalid_chars}\n\t{' '*start_index_error+'^^^^'}")
    
    params, tokens = get_function_params(characters, tail)
    body, tokens = get_function_body(characters, tokens)
    
    node = FunctionDeclaration(loc_={}, range_=[], id_=identifier.value_, params_=params, body_=body)
    return node, tokens

def get_function_body(characters: str, tokens: List[Token]):
    head, *tail = tokens
    if head.tokentype_ == TokenTypes.NEW_LINE:
        head, *tail = tail
    if head.tokentype_ != TokenTypes.TAB:
        return [], tail
    head, *tail = tail
    if head.tokentype_ != TokenTypes.LINE_NO:
        line_no_error       = head.loc_["start"]["line"]
        start_index_error   = head.loc_["start"]["index"]
        invalid_chars       = characters.split("\n")[head.loc_["start"]["line"]-1]
        raise Exception(f"Expected line nr. in function body (eg. 1., 2., 3.)\nFile <placeholder>, line {line_no_error}\n\t{invalid_chars}\n\t{' '*start_index_error+'^^^^'}")
    head, *_ = tail
    # if head.tokentype_ == TokenTypes.VARIABLE_DECLARATION: 
    #     node, tokens = parse_variable_declaration(characters, tail)
    if head.tokentype_ == TokenTypes.RETURN:
        node, tokens = parse_return_statement(characters, tail)
        return node, tokens
    if head.tokentype_ == TokenTypes.VARIABLE_DECLARATION:
        node, tokens = parse_variable_declaration(characters, tail)
        nodes, tokens = get_function_body(characters, tokens)
        return [node] + [nodes], tokens
    

def parse_return_statement(characters: str, tokens: List[Token]):
    head, expression, *tail = tokens
    if expression.tokentype_ not in (TokenTypes.IDENTIFIER, TokenTypes.MINUS, TokenTypes.PLUS, TokenTypes.INT, TokenTypes.FLOAT, TokenTypes.LEFT_PARENTHESIES):
        line_no_error       = expression.loc_["start"]["line"]
        start_index_error   = expression.loc_["start"]["index"]
        invalid_chars       = characters.split("\n")[expression.loc_["start"]["line"]-1]
        raise Exception(f"Expected expression after 'exit' statement\nFile <placeholder>, line {line_no_error}\n\t{invalid_chars}\n\t{' '*start_index_error+'^^^^'}")
    head, *tail = tokens
    node, tokens = parse_expr(tail)
    node = ReturnStatement(loc_={},range_=[], argument_=node)
    return node, tokens


def get_function_params(characters: str, tokens: List[Token]):
    head, *tail = tokens
    if head.tokentype_ == TokenTypes.INDENTATION :
        head, *tail = tail
        if head.tokentype_ != TokenTypes.NEW_LINE:
            line_no_error       = head.loc_["start"]["line"]
            start_index_error   = head.loc_["start"]["index"]
            invalid_chars       = characters.split("\n")[head.loc_["start"]["line"]-1]
            raise Exception(f"Expected newline '––>' after function declaration\nFile <placeholder>, line {line_no_error}\n\t{invalid_chars}\n\t{' '*start_index_error+'^^^^'}")
        return [], tail
    if head.tokentype_ == TokenTypes.NEW_LINE:
        line_no_error       = head.loc_["start"]["line"]
        start_index_error   = head.loc_["start"]["index"]
        invalid_chars       = characters.split("\n")[head.loc_["start"]["line"]-1]
        raise Exception(f"Expected '––>' after function declaration\nFile <placeholder>, line {line_no_error}\n\t{invalid_chars}\n\t{' '*start_index_error+'^^^^'}")
    if head.tokentype_ != TokenTypes.SEPARATOR:
        line_no_error       = head.loc_["start"]["line"]
        start_index_error   = head.loc_["start"]["index"]
        invalid_chars       = characters.split("\n")[head.loc_["start"]["line"]-1]
        raise Exception(f"Expected '|' after variable declaration\nFile <placeholder>, line {line_no_error}\n\t{invalid_chars}\n\t{' '*start_index_error+'^^^^'}")
    head, *tail = tail
    if head.tokentype_ != TokenTypes.VARIABLE_DECLARATION:
        line_no_error       = head.loc_["start"]["line"]
        start_index_error   = head.loc_["start"]["index"]
        invalid_chars       = characters.split("\n")[head.loc_["start"]["line"]-1]
        raise Exception(f"Expected 'parameter declaration' after function separator\nFile <placeholder>, line {line_no_error}\n\t{invalid_chars}\n\t{' '*start_index_error+'^^^^'}")
    head, *tail = tail
    if head.tokentype_ != TokenTypes.IDENTIFIER:
        line_no_error       = head.loc_["start"]["line"]
        start_index_error   = head.loc_["start"]["index"]
        invalid_chars       = characters.split("\n")[head.loc_["start"]["line"]-1]
        raise Exception(f"Expected 'identifier' after function parameter declaration\nFile <placeholder>, line {line_no_error}\n\t{invalid_chars}\n\t{' '*start_index_error+'^^^^'}")
    param =  [Identifier(loc_={}, range_=[], name_=head.value_)]
    params, tokens = get_function_params(characters, tail)
    return (param + params, tokens)


A = TypeVar('A')
def parse(characters: str, tokens: List[A], index: int = 0):
    head, *tail = tokens
    if head.tokentype_ == TokenTypes.LINE_NO:
        head, *_ = tail
        if head.tokentype_ == TokenTypes.VARIABLE_DECLARATION: 
            node, tokens = parse_variable_declaration(characters, tail)
            return [node] + parse(characters, tokens)
    if head.tokentype_ == TokenTypes.FUNCTION_DECLARATION:
        node, tokens = parse_function_declaration(characters, tokens)
        return [node] + parse(characters, tokens)
    if head.tokentype_ == TokenTypes.NEW_LINE:
        return parse(characters, tail)
    if head.tokentype_ == TokenTypes.EOF:
        return []
    print(head)
    raise Exception("Not implemented yet")
    

def sort(tokens):
    sorted_tokens = []
    tokens_in_line = []
    for token in tokens:
        tokens_in_line.append(token)
        if token.tokentype_ == TokenTypes.NEW_LINE:
            sorted_tokens.append(tokens_in_line)
            tokens_in_line = []
    sorted_tokens.append(tokens_in_line)
   
    for i in range(len(sorted_tokens)):
        if sorted_tokens[i][0].tokentype_ not in (TokenTypes.LINE_NO, TokenTypes.FUNCTION_DECLARATION, TokenTypes.NEW_LINE, TokenTypes.EOF, TokenTypes.TAB):
            raise Exception("Error, codeline must start with a number: (eg. 1.,2.,3.) or must be a function declaration")
    
    code_lines = list(filter(lambda token: token[0].tokentype_ == TokenTypes.LINE_NO, sorted_tokens))
    eof = list(filter(lambda token: token[0].tokentype_ == TokenTypes.EOF, sorted_tokens))
    other = list(filter(lambda token: token[0].tokentype_ != TokenTypes.LINE_NO and token[0].tokentype_ !=  TokenTypes.EOF, sorted_tokens))
    code_lines = sorted(code_lines, key=lambda x: int(x[0].value_[:-1]))
    return other + code_lines + eof
    # return sorted_tokens


if __name__=="__main__":
    # if len(sys.argv) <= 1:
    #     print("No source file provided!")
    #     exit()

    with open("simple_language.py", 'rb') as f: #"new_language.py"
        code = f.read().decode("utf-8")

    tokens = lex(code, search_match, TokenExpressions)
    tokens = list(filter(lambda token: token.tokentype_ != TokenTypes.NONE, tokens))

    print("Tokens:")
    # list(map(print, tokens))
    sorted_tokens = sort(tokens)
    merged = list(itertools.chain(*sorted_tokens))
    print("\n")

    parsed = parse(code, merged)
    program = Program(loc_={'start': {'line': 1, 'index': 0}, "end":{"line":tokens[-1].loc_["start"]["line"], "index":tokens[-1].loc_["start"]["index"]}}, range_=[0, len(code)], body_=parsed)
    print(program)