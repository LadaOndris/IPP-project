
from .return_codes import *

class Instruction:
    
    def __init__(self, opcode, arguments, order):
        self.opcode = opcode
        self.arguments = arguments
        self.order = order
        
    def __lt__(self, other):
        if self.order == other.order:
            raise InterpretException('Duplicit order', ReturnCodes.INVALID_INPUT)
        return self.order < other.order
