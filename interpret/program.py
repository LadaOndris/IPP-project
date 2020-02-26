
import xml.etree.ElementTree as et
from .argument import Argument
from .instruction import Instruction

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
            opcode = child.attrib['opcode']
            order = int(child.attrib['order'])
            instr = Instruction(opcode, arguments, order)
            instructions.append(instr)
        instructions.sort()
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
    
    def getInstructions(self):
        return self.instructions
