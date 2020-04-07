
import xml.etree.ElementTree as et
from .argument import Argument
from .instruction import Instruction
from .return_codes import *
import re
import collections
import sys

"""
The Program class represents given program.
It loads and parses an xml file.
After parsing the file, all instructions of the program are available.
"""
class Program:
    
    """
    inputFile is an xml file representing the program to be loaded
    """
    def __init__(self, inputFile):
        self.__parseInput(inputFile)
        
    """
    Loads the current program from given xml file.
    
    inputFile is an xml file
    """
    def __parseInput(self, inputFile):
        try:
            root = et.parse(inputFile).getroot()
        except:
            raise InterpretException('Invalid xml structure', ReturnCodes.INVALID_XML_STRUCTURE)
            
        try:
            self.__parseInstructions(root)
        except InterpretException:
            raise
        except:
            raise InterpretException('Bad xml input', ReturnCodes.INVALID_INPUT)
            
    
    """
    Parses instructrions and its attributes of the program.
    root is the root element of the xml
    """
    def __parseInstructions(self, root):
        self.instructions = []
        for attrName in root.attrib:
            if re.match('^(language|description|name)$', attrName) is None:
                raise InterpretException('Invalid program attribute name', ReturnCodes.INVALID_INPUT)
            
        for child in root:
            if child.tag != 'instruction':
                raise InterpretException('Bad xml input', ReturnCodes.INVALID_INPUT)
            arguments = self.__parseArguments(child)
            opcode = child.attrib['opcode']
            order = int(child.attrib['order'])
            if order < 0:
                raise InterpretException('Negative order', ReturnCodes.INVALID_INPUT)
            if len(child.attrib) > 2:
                raise InterpretException('Negative order', ReturnCodes.INVALID_INPUT)
            instr = Instruction(opcode, arguments, order)
            self.instructions.append(instr)
        self.instructions.sort()
     
    """
    Parses arguments for the given instruction element.
    Returns all arguments of the instruction.
    instructionElement is an xml element representing instruction
    """
    def __parseArguments(self, instructionElement):
        arguments = {}
        for argElement in instructionElement:
            argument = self.__parseArgument(argElement)
            
            if re.match('^(arg1|arg2|arg3)$', argElement.tag) is None:
                raise InterpretException('Invalid argument element tag', ReturnCodes.INVALID_INPUT)
            
            if argElement.tag in arguments:
                raise InterpretException('Already defined argument', ReturnCodes.INVALID_INPUT)
            
            arguments[argElement.tag] = argument
        
        orderedArguments = collections.OrderedDict(sorted(arguments.items()))
        for index, (key, value) in enumerate(orderedArguments.items()):
            if key != F"arg{index + 1}":
                raise InterpretException('Missing argument', ReturnCodes.INVALID_INPUT)
            yield value
            
    """
    Creates a new instance of the Argument class.
    If the type of the argument is nil or None, the value of the argument
    is changed to an empty string.
    """
    def __parseArgument(self, argElement):
        type = argElement.attrib["type"]
        value = argElement.text
        if (type == "nil"):
            value = ""
        if (value == None):
            value = ""
        return Argument(type, value)
    
    """
    Returns all instructions.
    """
    def getInstructions(self):
        return self.instructions
