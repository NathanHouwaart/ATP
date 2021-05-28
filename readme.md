# Alt-U Programming Language
This repository contains the lexer, parser and interpreter for the Alt-U programming languag. Why, Alt-U? Good question! This is because the language features a combination of Alt and Unicode characters which make up the whole syntax. This language is touring complete; it can perform algorithmic calculations, it can loop, it can check wether two expression are equal and it can execute conditional code.

## Grammar
The grammar of the Alt-U language is written in the so called Backus-Naur Form. This is an abstract way of writing down the functions of the programming language. More information about the Backus-Naur form can be found [here](https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form) 

### Syntax Rules
```
<program>::={<statement>*}

<statement>::=<assignment> | <if_statement> | <call_statement> | <return_statement> | <function>

<function>::= ƒ <identifier> ––> {<statements>+} 
            | ƒ <identifier> {(<separator> α <identifier>)+} ––> {<statements>+} <return_statement>

<call_statement>::= ✆ <identifier> ✆ 
                  | ✆ <identifier> <expression> {(<separator> <expression>)*} ✆

<variable_declaration>::= 📁 <identifier> = <expression>

<return_statement>::= ⮐ <expression> ⮐

<if_statement>::= ? <expression> ––> {<statements>+} ¿
                | ? <expression> ––> {<statements>+} {(⁈ <expression> ––> {<statements>+})*} ⁇ {<statements>+} ¿

<expression>::= <identifier> | <number> | <left_parenthesies> <expr> <right_parenthesies> | <call_statement> |-<expr> | +<expr> | <expr> <operator> <expr>
```

### Lexical Rules
```
<operator>::= + | - | * | / | = | < | > | ==
<identifier>::= <letter> | <identifier><letter> | <identifer><digit>
<digit>::= 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
<letter>::= a | b | c | d | ... | A | B | C | D | ..
<number>::=<digit>+
<separator>::= |
left_parenthesies::= <
right_parenthesies::= >
```

## How to use?
This section will explain how every individual part of the programming language (lexer, parser, interpreter) can be run. Note that every code sample can be run from either the [root directory](.) or the directory they are located in.
### Lexer
The lexer can is located in the [lexer.py](lexer_module/lexer.py) file in the [lexer_module](lexer_module) folder. To use the lexer, provide a source file with Alt-U code like so:
`python3 lexer.py <filename>`  
The lexer will print all the lexed tokens to the command line. Example:
```
$ python3 lexer_module/lexer.py tests/code_samples/valid/unary_expression/unary_expression_int.txt
Token(loc_={'start': {'line': 1, 'index': 0}, 'end': {'line': 1, 'index': 1}}, range_=[0, 1], value_='📁', tokentype_=<TokenTypes.VARIABLE_DECLARATION: 3>)
Token(loc_={'start': {'line': 1, 'index': 1}, 'end': {'line': 1, 'index': 2}}, range_=[1, 2], value_=' ', tokentype_=<TokenTypes.NONE: 0>)
Token(loc_={'start': {'line': 1, 'index': 2}, 'end': {'line': 1, 'index': 6}}, range_=[2, 6], value_='test', tokentype_=<TokenTypes.IDENTIFIER: 23>)
Token(loc_={'start': {'line': 1, 'index': 6}, 'end': {'line': 1, 'index': 7}}, range_=[6, 7], value_=' ', tokentype_=<TokenTypes.NONE: 0>)
Token(loc_={'start': {'line': 1, 'index': 7}, 'end': {'line': 1, 'index': 8}}, range_=[7, 8], value_='=', tokentype_=<TokenTypes.IS: 5>)
Token(loc_={'start': {'line': 1, 'index': 8}, 'end': {'line': 1, 'index': 9}}, range_=[8, 9], value_=' ', tokentype_=<TokenTypes.NONE: 0>)
Token(loc_={'start': {'line': 1, 'index': 9}, 'end': {'line': 1, 'index': 10}}, range_=[9, 10], value_='-', tokentype_=<TokenTypes.MINUS: 7>)
Token(loc_={'start': {'line': 1, 'index': 10}, 'end': {'line': 1, 'index': 12}}, range_=[10, 12], value_='20', tokentype_=<TokenTypes.INT: 21>)
Token(loc_={'start': {'line': 1, 'index': 12}, 'end': {'line': 1, 'index': 15}}, range_=[12, 15], value_='\x00', tokentype_=<TokenTypes.EOF: 24>)
```

### Parser
The parser files are located in the [parser_module](parser_module) folder. The parser has been split up in multiple files to split certain parser functionality. The main parser is located in the [parser.py](parser_module/parser.py) file. Based on the token found, the parser will call functions out of one of the [parser_submodules](parser_module/parser_submodules) folder. To use the parser, provide a source file with the Alt-U code like so:
`python3 parser.py <filename>`  

The parser will generate an Abstract Syntax Tree (AST) and generates a file named "pretty_printed.json" which contains a pretty printed version of the AST. The pretty_printed.json file will be generated in the same folder from which the program was executed. Example of an AST:
```
$ python3 parser_module/parser.py tests/code_samples/valid/program/fibonachi.txt
  
```
<details>
<summary>Content of the AST</summary>

```json
{"Program":{
    "loc_":{"start": {"line": 1, "index": 0}, "end": {"line": 7, "index": 25}},
    "range_":[0, 137],
    "body_":{
        "FunctionDeclaration":{
            "loc_":{"start": {"line": 1, "index": 0}, "end": {"line": 5, "index": 2}},
            "range_":[0, 108],
            "id_":"fibonachi",
            "params_":{
                "Identifier":{
                    "loc_":{"start": {"line": 1, "index": 16}, "end": {"line": 1, "index": 17}},
                    "range_":[16, 17],
                    "name_":"n"
                }
            },
            "body_":{
                "BlockStatement":{
                    "loc_":{"start": {"line": 2, "index": 4}, "end": {"line": 4, "index": 47}},
                    "range_":[27, 104],
                    "body_":{
                        "IfStatement":{
                            "loc_":{"start": {"line": 2, "index": 4}, "end": {"line": 3, "index": 15}},
                            "range_":[27, 55],
                            "test_":{
                                "BinaryExpression":{
                                    "loc_":{"start": {"line": 2, "index": 6}, "end": {"line": 2, "index": 11}},
                                    "range_":[29, 34],
                                    "operator_":"TokenTypes.SMALLER_THAN",
                                    "left_":{
                                        "Identifier":{
                                            "loc_":{"start": {"line": 2, "index": 6}, "end": {"line": 2, "index": 7}},
                                            "range_":[29, 30],
                                            "name_":"n"
                                        }
                                    },
                                    "right_":{
                                        "Literal":{
                                            "loc_":{"start": {"line": 2, "index": 10}, "end": {"line": 2, "index": 11}},
                                            "range_":[33, 34],
                                            "value_":2,
                                            "raw_":2
                                        }
                                    }
                                }
                            },
                            "consequent_":{
                                "BlockStatement":{
                                    "loc_":{"start": {"line": 3, "index": 8}, "end": {"line": 3, "index": 13}},
                                    "range_":[48, 53],
                                    "body_":{
                                        "ReturnStatement":{
                                            "loc_":{"start": {"line": 3, "index": 8}, "end": {"line": 3, "index": 13}},
                                            "range_":[48, 53],
                                            "argument_":{
                                                "Identifier":{
                                                    "loc_":{"start": {"line": 3, "index": 10}, "end": {"line": 3, "index": 11}},
                                                    "range_":[50, 51],
                                                    "name_":"n"
                                                }
                                            }
                                        }
                                    }
                                }
                            },
                            "alternate_":{
                                
                            }
                        },
                        "ReturnStatement":{
                            "loc_":{"start": {"line": 4, "index": 4}, "end": {"line": 4, "index": 47}},
                            "range_":[61, 104],
                            "argument_":{
                                "BinaryExpression":{
                                    "loc_":{"start": {"line": 4, "index": 7}, "end": {"line": 4, "index": 44}},
                                    "range_":[64, 101],
                                    "operator_":"TokenTypes.PLUS",
                                    "left_":{
                                        "CallExpression":{
                                            "loc_":{"start": {"line": 4, "index": 7}, "end": {"line": 4, "index": 24}},
                                            "range_":[64, 81],
                                            "arguments_":{
                                                "BinaryExpression":{
                                                    "loc_":{"start": {"line": 4, "index": 19}, "end": {"line": 4, "index": 22}},
                                                    "range_":[76, 79],
                                                    "operator_":"TokenTypes.MINUS",
                                                    "left_":{
                                                        "Identifier":{
                                                            "loc_":{"start": {"line": 4, "index": 19}, "end": {"line": 4, "index": 20}},
                                                            "range_":[76, 77],
                                                            "name_":"n"
                                                        }
                                                    },
                                                    "right_":{
                                                        "Literal":{
                                                            "loc_":{"start": {"line": 4, "index": 21}, "end": {"line": 4, "index": 22}},
                                                            "range_":[78, 79],
                                                            "value_":1,
                                                            "raw_":1
                                                        }
                                                    }
                                                }
                                            },
                                            "callee_":{
                                                "Identifier":{
                                                    "loc_":{"start": {"line": 4, "index": 9}, "end": {"line": 4, "index": 18}},
                                                    "range_":[66, 75],
                                                    "name_":"fibonachi"
                                                }
                                            }
                                        }
                                    },
                                    "right_":{
                                        "CallExpression":{
                                            "loc_":{"start": {"line": 4, "index": 27}, "end": {"line": 4, "index": 44}},
                                            "range_":[84, 101],
                                            "arguments_":{
                                                "BinaryExpression":{
                                                    "loc_":{"start": {"line": 4, "index": 39}, "end": {"line": 4, "index": 42}},
                                                    "range_":[96, 99],
                                                    "operator_":"TokenTypes.MINUS",
                                                    "left_":{
                                                        "Identifier":{
                                                            "loc_":{"start": {"line": 4, "index": 39}, "end": {"line": 4, "index": 40}},
                                                            "range_":[96, 97],
                                                            "name_":"n"
                                                        }
                                                    },
                                                    "right_":{
                                                        "Literal":{
                                                            "loc_":{"start": {"line": 4, "index": 41}, "end": {"line": 4, "index": 42}},
                                                            "range_":[98, 99],
                                                            "value_":2,
                                                            "raw_":2
                                                        }
                                                    }
                                                }
                                            },
                                            "callee_":{
                                                "Identifier":{
                                                    "loc_":{"start": {"line": 4, "index": 29}, "end": {"line": 4, "index": 38}},
                                                    "range_":[86, 95],
                                                    "name_":"fibonachi"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "VariableDeclaration":{
            "loc_":{"start": {"line": 7, "index": 0}, "end": {"line": 7, "index": 25}},
            "range_":[112, 137],
            "id_":"test",
            "init_": {
                "CallExpression":{
                    "loc_":{"start": {"line": 7, "index": 9}, "end": {"line": 7, "index": 25}},
                    "range_":[121, 137],
                    "arguments_":{
                        "Literal":{
                            "loc_":{"start": {"line": 7, "index": 21}, "end": {"line": 7, "index": 23}},
                            "range_":[133, 135],
                            "value_":15,
                            "raw_":15
                        }
                    },
                    "callee_":{
                        "Identifier":{
                            "loc_":{"start": {"line": 7, "index": 11}, "end": {"line": 7, "index": 20}},
                            "range_":[123, 132],
                            "name_":"fibonachi"
                        }
                    }
                }
            }
        }
    }
}}
```
</details>

### Interpreter
The interpreter can is located in the [interpreter.py](interpreter_module/interpreter.py) file in the [interpreter_module](interpreter_module) folder. To use the interpreter, provide a source file with Alt-U code like so:
`python3 interpreter.py <filename>`  
The interpreter will then execute the code. If a print statement is present in the privided Alt-U source file, the program will print something out to the terminal. Example of an interpreted source file:
```
$ python3 interpreter_module/interpreter.py fibonachi.txt
610
program finished in 0.71961 s

```

### Error messaging
The Alt-U programming Language comes with a wide veriaty of error messages. Error messages range from: invalid syntax messages and undefined identifier messages. The error messaging system will print out an error message which exactly pinpoints where the error message is located. Examples of error messages are:

```
$ python3 python3 interpreter_module/interpreter.py tests/code_samples/invalid/chained_expression/missing_left_parenthesies.txt
<ptyhon exception stack trace>
Exception: Invalid Syntax
File <placeholder>, line 1
        📁 test = 10 * 2 + 4>
                            ^
```

```
$ python3 interpreter_module/interpreter.py tests/code_samples/invalid/call_expression/call_invalid_separator.txt
<ptyhon exception stack trace>
Exception: Missing '|' between multiple parameters
File <placeholder>, line 1
        ✆ fib param1 param2 ✆
                     ^^^^^^
```

```
$ python3 interpreter_module/interpreter.py fibonachi.txt
<ptyhon exception stack trace>
Exception: Expected '¿' after if statement end
File <placeholder>, line 4
    📁 var1 = 10
               ^^^
```

More error messages can be generated by running the interpreter with any of the invalid code samples located in [test/code_samples/invalid](test/code_samples/invalid)

## Examples
There are tons of code samples which are included in this repository, ranging from simple expressions, if-statements, function-calls, to whole programs. They can be found in the [code samples directory](tests/code_samples).
Two main examples are included in the root directory of this repository. An explanation of the two code samples will be given below:

### Fibonachi.txt
program:
```
ƒ fibonachi | α n ––>
    ? n ▼ 2 ––>
        ⮐ n ⮐ ¿
    ⮐ <✆ fibonachi n-1 ✆ + ✆ fibonachi n-2 ✆> ⮐
––

📁 test = ✆ fibonachi 15 ✆
✆ 🖨 test ✆
```
Explanation: First, a function is declarated. This is done with the `ƒ` symbol. This is followed by an identifier `fibonachi`. Then, a `|` and `α` token is required to indicate a function parameter is coming up. The function parameter is called `n`. The function declaration is then closed with a `––>` statement.  
The next few lines (untill `––`) make up the function body: 
- We can see the body starts with an if-statement. If n is smaller than 2, return n, else continue
- Return fibonachi(n-1) + fibonachi(n-1)
- `––`: end of the function definition

After that, some regular code:
- Assign the result of fibonachi(15) to the variable `test`
- Print out thhe value of `test`

### double_recursive.txt
program:
```
ƒ odd | α n ––>
    ? n == 0 ––>
        ⮐ 0 ⮐ ¿
    ⮐ ✆ even n-1 ✆ ⮐
––

ƒ even | α n ––>
    ? n == 0 ––>
        ⮐ 1 ⮐ ¿
    ⮐ ✆ odd n-1 ✆ ⮐
––

📁 test = ✆ even 15 ✆
✆ 🖨 test ✆
```
Explanation: First, a function is declarated. This is done with the `ƒ` symbol. This is followed by an identifier `odd`. Then, a `|` and `α` token is required to indicate a function parameter is coming up. The function parameter is called `n`. The function declaration is then closed with a `––>` statement.  
The next few lines (untill `––`) make up the function body: 
- We can see the body starts with an if-statement. If n is equal to 0, return 0, else continue
- return even(n-1)
- `––`: end of the function definition

Then, another function is declarated. This is done with the `ƒ` symbol. This is followed by an identifier `even`. Then, a `|` and `α` token is required to indicate a function parameter is coming up. The function parameter is called `n`. The function declaration is then closed with a `––>` statement.  
The next few lines (untill `––`) make up the function body: 
- We can see the body starts with an if-statement. If n is equal to 0, return 1, else continue
- return odd(n-1)
- `––`: end of the function definition

After that, some regular code:
- Assign the result of even(15) to the variable `test`
- Print out thhe value of `test`

## Tests
To run the tests, run the following command in the root directory:  
`python3 tests\test_all.py` or `python3 test_all.py` in the [tests](tests) directory


## List of symbols:
Please take note of the following:
**Note:!! ––> and --> are NOT the same. --> can be directly typed with your keyboard (this is the minus key), whilst ––> cannot be directly typed with your keybord**
**Note:!! –– and -- are NOT the same. -- can be directly typed with your keyboard (this is the minus key), whilst –– cannot be directly typed with your keybord**
**Why?, just because :D**
|Symbol |Description|
|-----|--------|
| ƒ     | Function Start       |
| ––>   | Indentation (needed after if, elif, else statements, functions) |
| ––    | Function End |
| 📁    | Variable Declaration |
| α     | Function parameter in parameter list |
| =     | Assign |
| ==    | Is Equal|
| ▲     | Greater Than |
| ▼     | Smaller Than | 
| +     | Plus |
| -     | Minus|
| /     | Divide |
| *     | Multiply |
| \|    | Separator | 
| ∨     | Or | 
| ∧     | And |
| <     | Left Parenthesies |
| >     | Right Parenthesies |
| ?     | If | 
| ⁈     | Else If | 
| ⁇     | Else |  
| ¿     | If-End |
| 🖨    | Print |
| ✆    | Call | 
| ⮐     | Return | 
