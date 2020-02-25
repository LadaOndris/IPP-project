
from .operand import *
from .return_codes import *

class Instruction:
    
    def __init__(self, operands, expectedOperands, processor):
        self.operands = operands
        self.expectedOperands = expectedOperands
        self.processor = processor
        self.__checkOperands()
        
    def __checkOperands(self):
        if len(self.operands) != len(self.expectedOperands):
            raise InterpretException("Operands don't match", ReturnCodes.INVALID_INPUT)
        for given, expected in zip(self.operands, self.expectedOperands):
            if not isinstance(given, expected):
                raise InterpretException("Operands don't match", ReturnCodes.INVALID_INPUT)
        
    def execute(self):
        raise NotImplementedError('Abstract method')
    
class DefvarInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ VariableOperand ]
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        self.processor.frameModel.defvar(self.operands[0].getFrameName())

class MoveInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ VariableOperand, SymbolOperand ]
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):        
        destinationOperand = self.operands[0]
        sourceOperand = self.operands[1]
        variable = self.processor.frameModel.getVariable(destinationOperand.getFrameName())
        variable.set(sourceOperand.getValue(), sourceOperand.getType())
    
class WriteInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ SymbolOperand ]
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        sourceOperand = self.operands[0]
        self.__writeValue(sourceOperand.getValue(), sourceOperand.getType())
        
    def __writeValue(self, value, type):
        if type == 'bool':
            print('true' if value else 'false', end='')
        elif type == 'nil':
            print('', end='')
        elif type == 'int' or type == 'string':
            print(value, end='')
        else:
            raise InterpretException("Invalid argument type", ReturnCodes.INVALID_INPUT)
            
class ReadInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ SymbolOpernad, TypeOperand]
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        toOperand = self.operands[0]
        typeOperand = self.operands[1]
        variable = self.processor.frameModel.getVariable(toOperand.getFrameName())
        value = self.__readValue(typeOperand.getValue())
        variable.set(value, typeOperand.getValue())
    
    def __readValue(self, type):
        value = input()
        return self.__convertToType(value, type)
        
    def __convertToType(self, value, type):
        if type == 'int':
            return int(value)
        if type == 'bool':
            return value.lower() == 'true'
        if type == 'string':
            return value
        raise InterpretException("Invalid type: " + type, ReturnCodes.INVALID_INPUT)

class CreateframeInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = []
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        self.processor.frameModel.resetTemporaryFrame()
    
class PushframeInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = []
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        self.processor.frameModel.pushTempFrameToLocalFrameStack()

class PopframeInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = []
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        self.processor.frameModel.popFromLocalFrameStackToTempFrame()
    
class CallInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ LabelOperand ]
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        self.processor.instructionCounter.pushCallstack()
        self.processor.instructionCounter.jumpTo(self.operands[0].getValue())
   
class ReturnInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = []
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        self.processor.instructionCounter.popCallstack()
        
class LabelInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ LabelOperand ]
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        pass
        
class JumpInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ LabelOperand ]
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        label = self.operands[0].getValue()
        self.processor.instructionCounter.jumpTo(label)
    
class JumpifeqInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ LabelOperand, SymbolOperand, SymbolOperand ]
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        label = self.operands[0].getValue()
        op1type = self.operands[1].getType()
        op2type = self.operands[2].getType()
        if op1type != op2type and op1type != 'nil' and op2type != 'nil':
            raise InterpretException('Types differ', ReturnCodes.BAD_OPERANDS)
        if self.operands[1].getValue() == self.operands[2].getValue():
            self.processor.instructionCounter.jumpTo(label)

class JumpifneqInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ LabelOperand, SymbolOperand, SymbolOperand ]
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        label = self.operands[0].getValue()
        op1type = self.operands[1].getType()
        op2type = self.operands[2].getType()
        if op1type != op2type and op1type != 'nil' and op2type != 'nil':
            raise InterpretException('Types differ', ReturnCodes.BAD_OPERANDS)
        if self.operands[1].getValue() != self.operands[2].getValue():
            self.processor.instructionCounter.jumpTo(label)

class ExitInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ SymbolOperand ]
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        exitCode = self.operands[0].getValue()
        if exitCode >= 0 and exitCode <= 49:
            self.processor.stop(exitCode)
        else:
            raise InterpretException('Invalid exit code', ReturnCodes.BAD_OPERAND_VALUE)

class TypeInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ VariableOperand, SymbolOperand ]
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):  
        variable = self.processor.frameModel.getVariable(self.operands[0].getFrameName())
        type = self.operands[1].getType()
        if type == None:
            type = ''
        variable.set(type, 'string')
        
class Processor:
    
    def __init__(self, frameModel, operandFactory):
        self.frameModel = frameModel
        self.__operandFactory = operandFactory
        self.instructionCounter = InstructionCounter()
        self.__stopCode = None
        
    def execute(self, rawInstructions):
        self.__createInstructions(rawInstructions)
        self.instructionCounter.setInstructions(self.instructions)
    
        while self.instructionCounter.nextInstruction() and self.__stopCode == None:
            self.instructionCounter.executeCurrentInstruction()
        
    def __createInstructions(self, rawInstructions):
        self.instructions = []
        for rawInstr in rawInstructions: 
            instruction = self.__createInstruction(rawInstr.opcode, rawInstr.arguments)
            self.instructions.append(instruction)
        
    def __createInstruction(self, opcode, rawOperands):
        operands = self.__createOperands(rawOperands)
        className = opcode.capitalize() + "Instruction"
        try:
            return eval(className)(operands, self)
        except NameError:
            raise InterpretException('Unknown opcode', ReturnCodes.INVALID_INPUT)
    
    def __createOperands(self, rawOperands):
        operands = []
        for rawOperand in rawOperands:
            operand = self.__operandFactory.create(rawOperand)
            operands.append(operand)
        return operands
            
    def stop(self, code):
        self.__stopCode = code;
 
class InstructionCounter:
    
    def __init__(self):
        self.__counter = 0
        self.callStack = []
        
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
                    raise InterpretException('Label already exists', ReturnCodes.BAD_OPERAND_VALUE)
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
    
    def __incrementCounter(self):
        self.__counter += 1
        
    def __decrementCounter(self):
        self.__counter -= 1
        
    def pushCallstack(self):
        self.callStack.append(self.__counter + 1)
    
    def popCallstack(self):
        if len(self.callStack) == 0:
            raise InterpretException('Callstack is empty', ReturnCodes.MISSING_VALUE)
        self.__counter = self.callStack.pop()
        
    def jumpTo(self, label):
        if not label in self.labels:
            raise InterpretException('Label doesnt exist', ReturnCodes.BAD_OPERAND_VALUE)
        self.__counter = self.labels[label] 
    
        
    
    
    