"""
Created on Sat Feb 22 16:50:35 2020

@author: Ladislav Ondris

IPP project, an interpret of IPPcode20.
"""
import sys
import argparse
from interpret import *


def printHelp():
    print("test.php help:")
    print("--help                        Prints this help.")
    print("--source SOURCE               Path to the source file.")
    print("--input SOURCE                Path to the input file (meaning the stdin for the program).")

ap = argparse.ArgumentParser(add_help = False)
ap.add_argument("-s", "--source")
ap.add_argument("-i", "--input")
ap.add_argument("-h", "--help", action='store_true', default=False)
args = vars(ap.parse_args())

try:
    sourceOption = args["source"]
    inputOption = args["input"]
    helpOption = args['help']
    
    if sourceOption == None and inputOption == None:
        if helpOption == False:
            raise InterpretException('Some option have to be specified', ReturnCodes.SCRIPT_PARAMETER_ERROR)
        else:
            printHelp()
            exit(ReturnCodes.SUCCESS)
    elif helpOption == True:
        raise InterpretException('Cannot combine paramaters', ReturnCodes.SCRIPT_PARAMETER_ERROR)
    
    if sourceOption == None:
        sourceOption = sys.stdin
    
    if inputOption == None:
        inputFile = None
    else:
        inputFile = open(inputOption)
        sys.stdin = inputFile
        
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











        
