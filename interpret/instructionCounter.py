from .processor import *
from .return_codes import *
import sys

class InstructionCounter:
    
    def __init__(self):
        self.__counter = 0
        self.callStack = []
        self.executedInstructions = 0
        
    def setInstructions(self, instructions):
        self.__counter = 0
        self.instructions = instructions
        self.__findLabels()
    
    def __findLabels(self):
        labels = {}
        for index, instr in enumerate(self.instructions):
            if isinstance(instr, LabelInstruction):
                label = instr.operands[0].getValue()
                if label in labels:
                    raise InterpretException('Label already exists', ReturnCodes.SEMANTIC_ERROR)
                labels[label] = index
        self.labels = labels
                        
    def nextInstruction(self):
        if self.__counter < len(self.instructions):
            self.currentInstruction = self.instructions[self.__counter]
            self.__incrementCounter()
            return True
        else:
            return False
    
    def executeCurrentInstruction(self):
        self.currentInstruction.execute()
        self.executedInstructions += 1
        
    def __incrementCounter(self):
        self.__counter += 1
        
    def __decrementCounter(self):
        self.__counter -= 1
        
    def pushCallstack(self):
        self.callStack.append(self.__counter)
    
    def popCallstack(self):
        if len(self.callStack) == 0:
            raise InterpretException('Callstack is empty', ReturnCodes.MISSING_VALUE)
        self.__counter = self.callStack.pop()
        
    def jumpTo(self, label):
        if not label in self.labels:
            raise InterpretException('Label doesnt exist', ReturnCodes.SEMANTIC_ERROR)
        self.__counter = self.labels[label] 
    