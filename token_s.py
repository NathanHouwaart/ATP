class Token():
    def __init__(self, value, line_no, index, token_type, token_id):
        self.value = value
        self.line_no = line_no
        self.index = index
        self.token_type = token_type
        self.token_id = token_id

    def __repr__(self):
        return f"ID:{self.token_id:>3}\tType: {self.token_type:<30}\tLine:{self.line_no:>2}[{self.index:>2}]\tSymbol: {self.value}"

    
