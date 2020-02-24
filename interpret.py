"""
Created on Sat Feb 22 16:50:35 2020

@author: Ladislav Ondris

IPP project, an interpret of IPPcode20.
"""

import argparse
from enum import Enum
from interpret import *

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

ap = argparse.ArgumentParser()
ap.add_argument("-s", "--source")
ap.add_argument("-i", "--input")
args = vars(ap.parse_args())

frameModel = FrameModel()
processor = Processor(frameModel)
program = Program(args["source"])

processor.execute(program.getInstructions())












        
