"""
@file parser.py
@author Nathan Houwaart (nathan.houwaart@student.hu.nl)
@brief This file main parser functions
@version 0.1
@date 11-05-2021
"""
from collections import defaultdict

def determine_types(args, kwargs):
    return tuple([type(a) for a in args]), \
           tuple([(k, type(v)) for k,v in kwargs.items()])

function_table = defaultdict(dict)
def overload(arg_types=(), kwarg_types=()):
    def wrap(func):
        named_func = function_table[func.__name__]
        named_func[arg_types, kwarg_types] = func
        def call_function_by_signature(*args, **kwargs):
            return named_func[determine_types(args, kwargs)](*args, **kwargs)
        return call_function_by_signature
    return wrap


if __name__ == "__main__":
    @overload((str, int))
    def f(a,b):
        return a*b

    @overload((int, int, int))
    def f(a, b, c):
        return a + b + c


    print(f('a', 2))
    print(f(4, 2, 1))
