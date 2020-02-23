"""
Created on Sat Feb 22 16:50:35 2020

@author: Ladislav Ondris

IPP project, an interpret of IPPcode20.
"""

import argparse
import xml.etree.ElementTree as et
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
    
    def __init__(self, name, frame, value = None, type = None):
        self.name = name
        self.frame = frame
        self.value = value
        self.type = type
        
class Frame:
    def __init__(self):
        self.variables = {}
    
    def insertVariable(self, variable):
        self.variables[variable.name] = variable
        
    def getVariable(self, variableIdentifier):
        if variableIdentifier in self.variables:
            return self.variables[variableIdentifier]
        else:
            raise Exception("Unknown variable")


# Fetch, Decode, Execute
class Processor:

    def __init__(self):
        self.globalFrame = Frame()
        self.localFrameStack = []
        self.temporaryFrame = None

    def __createFrame(self):
        self.temporaryFrame = Frame()
    
    def __write(self, argument):
        if argument.type == 'var':
            variable = self.__getVariable(argument.value)
            self.__writeValue(variable.type, variable.value)
        else:
            self.__writeValue(argument.value, argument.type)
            
    def __writeValue(self, type):
        if argument.type == 'bool':
            print('true' if argument.value else 'false', end='')
        elif argument.type == 'nil':
            print('', end='')
        elif argument.type == 'int' or argument.type == 'string':
            print(argument.value, end='')
        else:
            raise Exception("Invalid argument type")
            
    def __read(self, toArgument, typeArgument):
        variable = self.__getVariable(toArgument.value)
        variable.value = self.__readValue(variable.type)
    
    def __readValue(self, type):
        value = input()
        return self.__convertToType(value, type)
        
    def __convertToType(value, type):
        if type == 'int':
            return int(value)
        if type == 'bool':
            return value.lower() == 'true'
        if type == 'string':
            return value
        raise Exception("Invalid type")
        
    def __getVariable(self, variable):
        frameName, variableIdentifier = variable.split('@', 1)
        frame = self.__getFrame(frameName)
        return frame.getVariable(variableIdentifier)
        
    def __getFrame(self, frameName):
        if frameName == "GF":
            return self.globalFrame
        elif frameName == "LF":
            return self.localFrameStack[0]
        elif frameName == "TF":
            return self.temporaryFrame
        else:
            raise Exception("Unknown frame")
    
    def execute(self, instruction):
        opcode = instruction.opcode
        if opcode == 'WRITE':
            self.__write(instruction.arguments[0])
        if opcode == 'READ':
            self.__read(instruction.arguments[0], instruction.arguments[1])
        else:
            raise Exception('Unknown instruction opcode')
        return
    
class Argument:
    
    def __init__(self, type, value):
        self.type = type
        self.value = value

class Instruction:
    
    def __init__(self, opcode, arguments):
        self.opcode = opcode
        self.arguments = arguments

class Program:
    
    def __init__(self, inputFile):
        self.__parseInput(inputFile)
        
    def __parseInput(self, inputFile):
        root = et.parse(inputFile).getroot()
        self.__parseInstructions(root)
        
    def __parseInstructions(self, root):
        instructions = []
        for child in root:
            arguments = self.__parseArguments(child)
            instr = Instruction(child.attrib['opcode'], arguments)
            instructions.append(instr)
        self.instructions = instructions    
        
    def __parseArguments(self, instructionElement):
        arguments = []
        for arg in instructionElement:
            arguments.append(self.__parseArgument(arg))
        return arguments
    
    def __parseArgument(self, argElement):
        type = argElement.attrib["type"]
        value = argElement.text
        if (type == "bool"):
            value = bool(value)
        elif (type == "nil"):
            value = ""
        return Argument(type, value)
    
    def instructionIterator(self):
        return iter(self.instructions)

ap = argparse.ArgumentParser()
ap.add_argument("-s", "--source")
ap.add_argument("-i", "--input")
args = vars(ap.parse_args())


processor = Processor()
program = Program(args["source"])


for instr in program.instructionIterator():
    processor.execute(instr)












        
