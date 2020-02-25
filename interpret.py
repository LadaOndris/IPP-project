"""
Created on Sat Feb 22 16:50:35 2020

@author: Ladislav Ondris

IPP project, an interpret of IPPcode20.
"""
import sys
import argparse
from interpret import *

ap = argparse.ArgumentParser()
ap.add_argument("-s", "--source")
ap.add_argument("-i", "--input")
args = vars(ap.parse_args())

try:
    frameModel = FrameModel()
    operandFactory = OperandFactory(frameModel)
    processor = Processor(frameModel, operandFactory)
    program = Program(args["source"])
    
    processor.execute(program.getInstructions())
except InterpretException as ex:
    print(ex.args[0], file=sys.stderr)
    exit(ex.args[1])
except Exception as ex:
    print(ex.args[0], file=sys.stderr)
    exit(ReturnCodes.INTERNAL_ERROR)











        
