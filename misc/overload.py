"""
@file overload.py
@author Nathan Houwaart (nathan.houwaart@student.hu.nl)
@brief This file contains the functions used to make the overload decorator
@version 0.1
@date 11-05-2021
"""
from collections import defaultdict

def determine_types(args, kwargs):
    """Function is used to determine the signature of the function called based on the parameters given"""
    return tuple([type(a) for a in args]), \
           tuple([(k, type(v)) for k,v in kwargs.items()])

function_table = defaultdict(dict)
def overload(arg_types=(), kwarg_types=()):
    """Overload wrapper. Used to overload a function with the same name, but with different parameter types"""
    def wrap(func):
        named_func = function_table[func.__name__]
        named_func[arg_types, kwarg_types] = func
        def call_function_by_signature(*args, **kwargs):
            return named_func[determine_types(args, kwargs)](*args, **kwargs)
        return call_function_by_signature
    return wrap