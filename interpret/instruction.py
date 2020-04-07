
from .return_codes import *

"""
The Instruction class represents a single instruction of the program.
It holds its opcode, arguments and execution order.
"""
class Instruction:
    
    def __init__(self, opcode, arguments, order):
        self.opcode = opcode
        self.arguments = arguments
        self.order = order
        
    def __lt__(self, other):
        if self.order == other.order:
            raise InterpretException('Duplicit order', ReturnCodes.INVALID_INPUT)
        return self.order < other.order
