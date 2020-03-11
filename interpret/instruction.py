
class Instruction:
    
    def __init__(self, opcode, arguments, order):
        self.opcode = opcode
        self.arguments = arguments
        self.order = order
        
    def __lt__(self, other):
        return self.order < other.order
