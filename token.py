from typing import *
from token_types import TokenTypes

class Token(NamedTuple):
    loc_: Dict[str, Dict[str,int]]
    range_: List[int]
    value_: str
    tokentype_: TokenTypes
    

# class Token():
#     def __init__(self, value, line_no, line_index_start, line_index_end, total_index, token_type):
#         self.value = value
#         self.line_no = line_no
#         self.index = index
#         self.line_
#         self.token_type = token_type

#     def __repr__(self):
#         return f"{self.token_type}, {repr(self.value)}"