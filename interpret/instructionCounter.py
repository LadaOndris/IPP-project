from .processor import *
from .return_codes import *
import sys

"""
InstructionCounter is responsible for maintaining the instruction
pointer. It provides methods for iterating through the instructions or
jumping to labels. 
"""
class InstructionCounter:
    
    """
    Initialize a new instrance of the InstructionCounter.
    """
    def __init__(self):
        self.__counter = 0
        self.callStack = []
        self.executedInstructions = 0
    
    """
    Set the instructions to work with.
    """
    def setInstructions(self, instructions):
        self.__counter = 0
        self.instructions = instructions
        self.__findLabels()

    """
    Enumerates through all isntructions and 
    finds all labels.
    """
    def __findLabels(self):
        labels = {}
        for index, instr in enumerate(self.instructions):
            if isinstance(instr, LabelInstruction):
                label = instr.operands[0].getValue()
                if label in labels:
                    raise InterpretException('Label already exists', ReturnCodes.SEMANTIC_ERROR)
                labels[label] = index
        self.labels = labels
              
    """
    Moves instruction pointer by one instruction.
    Returns True if there is an instruction, and False if 
    there are no more instructions.
    """         
    def nextInstruction(self):
        if self.__counter < len(self.instructions):
            self.currentInstruction = self.instructions[self.__counter]
            self.__incrementCounter()
            return True
        else:
            return False
    
    """
    Executes the current instruction pointed to by instruction pointer.
    """
    def executeCurrentInstruction(self):
        self.currentInstruction.execute()
        self.executedInstructions += 1
        
    def __incrementCounter(self):
        self.__counter += 1
        
    def __decrementCounter(self):
        self.__counter -= 1
      
    """
    Pushes the current position of instruction pointer to callstack.
    """
    def pushCallstack(self):
        self.callStack.append(self.__counter)
    
    """
    Pops a value from callstack and 
    sets the value as the current position of instruction pointer.
    Raises an exception if there is no value in the callstack.
    """
    def popCallstack(self):
        if len(self.callStack) == 0:
            raise InterpretException('Callstack is empty', ReturnCodes.MISSING_VALUE)
        self.__counter = self.callStack.pop()
    
    """
    Jumps to the specified label.
    Raises an exception if the label doesn't exist.
    """
    def jumpTo(self, label):
        if not label in self.labels:
            raise InterpretException('Label doesnt exist', ReturnCodes.SEMANTIC_ERROR)
        self.__counter = self.labels[label] 
    