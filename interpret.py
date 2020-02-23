"""
Created on Sat Feb 22 16:50:35 2020

@author: Ladislav Ondris

IPP project, an interpret of IPPcode20.
"""

import argparse
from enum import Enum

class ReturnCodes(Enum):
    SUCCESS = 0
    SCRIPT_PARAMETER_ERROR = 10
    INPUT_FILE_ERROR = 11
    OUTPUT_FILE_ERROR = 12
    INVALID_XML_STRUCTURE = 31
    INVALID_INPUT = 32
    SEMANTIC_ERROR = 52
    BAD_OPERANDS = 53
    UKNOWN_VARIABLE = 54
    INVALID_FRAME = 55
    MISSING_VALUE = 56
    BAD_OPERAND_VALUE = 57
    INVALID_STRING_OPERATION = 58
    
    
class Variable:
    
    def __init__(self, name, value, type):
        self.name = name
        self.value = value
        self.type = type
        

class Frame:
    variables = []
    
    def insertVariable(self, variable):
        variables.append(variable)


# Fetch, Decode, Execute
class Processor:

    def __init__(self):
        self.globalFrame = Frame()
        self.localFrameStack = []
        self.temporaryFrame = None

    def __createFrame(self):
        self.temporaryFrame = Frame()
    
    def execute(self, instruction):
        return
    


 

ap = argparse.ArgumentParser()
ap.add_argument("-s", "--source")
ap.add_argument("-b", "--soperand")
args = vars(ap.parse_args())

print(args)













        
