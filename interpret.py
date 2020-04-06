"""
Created on Sat Feb 22 16:50:35 2020

@author: Ladislav Ondris

IPP project, an interpret of IPPcode20.
"""
import sys, traceback
import argparse
from interpret import *

def printHelp():
    print("test.php help:")
    print("--help                        Prints this help.")
    print("--source SOURCE               Path to the source file.")
    print("--input SOURCE                Path to the input file (meaning the stdin for the program).")
    print("--stats SOURCE                Path to the file to write the statistics into.")
    print("--insts                       Write number of executed instructions to stats file.")
    print("--vars                        Write the maximum number of initialized variables to stats file.")

def printStatisticsToFile(filepath):
    try:
        statsfile = open(filepath, 'w')
    except:    
        raise InterpretException('Cannot open file', ReturnCodes.OUTPUT_FILE_ERROR)
    
    for arg in sys.argv:
        if arg == "--insts":
            statsfile.write(F"{instructionCounter.executedInstructions}\n")
        elif arg == "--vars":
            statsfile.write(F"{frameModel.maximumVariables}\n")
    statsfile.close()
    
ap = argparse.ArgumentParser(add_help = False)
ap.add_argument("--source")
ap.add_argument("--input")
ap.add_argument("--stats")
ap.add_argument("--insts", action='store_true', default=False)
ap.add_argument("--vars", action='store_true', default=False)
ap.add_argument("--help", action='store_true', default=False)
args = vars(ap.parse_args())

try:
    sourceOption = args["source"]
    inputOption = args["input"]
    helpOption = args['help']
    statsOption = args['stats']
    varsOption = args['vars']
    instsOption = args['insts']
    
    if varsOption == True or instsOption == True:
        if statsOption == None:
            raise InterpretException('--stats option wasn\'t specified', ReturnCodes.SCRIPT_PARAMETER_ERROR)
            
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
        try:
            inputFile = open(inputOption)
        except:
            raise InterpretException('Cannot open file', ReturnCodes.INPUT_FILE_ERROR)
        sys.stdin = inputFile
        
    frameModel = FrameModel()
    operandFactory = OperandFactory(frameModel)
    instructionCounter = InstructionCounter()
    processor = Processor(frameModel, operandFactory, instructionCounter, inputFile)
    program = Program(sourceOption)
    
    processor.execute(program.getInstructions())
    
    #print("Executed instructions:", instructionCounter.executedInstructions, file=sys.stderr)
    #print("Maximum variables:", frameModel.maximumVariables, file=sys.stderr)
    
    if statsOption != None:
        printStatisticsToFile(statsOption)
    
    if processor.stopCode == None:
        exit(0)
    else:
        exit(processor.stopCode)
        
except InterpretException as ex:
    print(ex.args[0], file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    exit(ex.args[1])
# except Exception as ex:
#     print(ex.args[0], file=sys.stderr)
#     exit(ReturnCodes.INTERNAL_ERROR)
    
        











        
