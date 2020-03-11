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
    sourceOption = args["source"]
    inputOption = args["input"]
    # helpOption = args['help']
    
    if sourceOption == None and inputOption == None:
        raise InterpretException('Some option have to be specified', ReturnCodes.SCRIPT_PARAMETER_ERROR)
    # elif helpOption != None:
        # raise InterpretException('Some option have to be specified', ReturnCodes.SCRIPT_PARAMETER_ERROR)
    
    if sourceOption == None:
        source = sys.stdin
        
    if inputOption != None:
        inputFile = open(inputOption)
        sys.stdin = inputFile
    else:
        inputFile = None
        
    frameModel = FrameModel()
    operandFactory = OperandFactory(frameModel)
    processor = Processor(frameModel, operandFactory, inputFile)
    program = Program(sourceOption)
    
    processor.execute(program.getInstructions())
    
    if processor.stopCode == None:
        exit(0)
    else:
        exit(processor.stopCode)
        
except InterpretException as ex:
    print(ex.args[0], file=sys.stderr)
    exit(ex.args[1])
# except Exception as ex:
#     print(ex.args[0], file=sys.stderr)
#     exit(ReturnCodes.INTERNAL_ERROR)











        
