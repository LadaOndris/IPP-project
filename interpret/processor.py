
from .operand import *
from .return_codes import *
import fileinput
import sys

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
        expectedOperands = [ SymbolOperand, TypeOperand]
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        toOperand = self.operands[0]
        typeOperand = self.operands[1]
        type = typeOperand.getValue()
        variable = self.processor.frameModel.getVariable(toOperand.getFrameName())
        try:
            value, type = self.__readValue(typeOperand.getValue())
        except:
            value = ''
            type = 'nil'
        variable.set(value, type)
    
    def __readValue(self, type):
        #file = self.processor.getInputFile()
        value = input()
        # if file == None:
        #     value = input()
        # else:
        #     value = file.readline().strip()
        #     if value == '':
        #         return '', 'nil'
        return self.__convertToType(value, type), type
        
    def __convertToType(self, value, type):
        if type == 'int':
            return int(value)
        if type == 'bool':
            return value.lower() == "true"
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
        super().__init__(operands, expectedOperands, processor)
        
    def execute(self):
        jumpToLabel = self.operands[0].getValue()
        self.processor.instructionCounter.pushCallstack()
        self.processor.instructionCounter.jumpTo(jumpToLabel)
   
class ReturnInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = []
        super().__init__(operands, expectedOperands, processor)
        
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
        val1 = self.operands[1].getValue()
        val2 = self.operands[2].getValue()
        
        op1type = self.operands[1].getType()
        op2type = self.operands[2].getType()
        if op1type != op2type and op1type != 'nil' and op2type != 'nil':
            raise InterpretException('Types differ', ReturnCodes.BAD_OPERANDS)
        if val1 == val2:
            self.processor.instructionCounter.jumpTo(label)

class JumpifneqInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ LabelOperand, SymbolOperand, SymbolOperand ]
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        label = self.operands[0].getValue()
        val1 = self.operands[1].getValue()
        val2 = self.operands[2].getValue()
        
        op1type = self.operands[1].getType()
        op2type = self.operands[2].getType()
        
        if op1type != op2type and op1type != 'nil' and op2type != 'nil':
            raise InterpretException('Types differ', ReturnCodes.BAD_OPERANDS)
        
        if val1 != val2:
            self.processor.instructionCounter.jumpTo(label)

class ExitInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ SymbolOperand ]
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        exitCode = self.operands[0].getValue()
        
        if self.operands[0].getType() != 'int':
            raise InterpretException('Invalid exit code operand', ReturnCodes.BAD_OPERANDS)
            
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
        
class ConcatInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ VariableOperand, SymbolOperand, SymbolOperand ]
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        str1 = self.operands[1].getValue()
        str2 = self.operands[2].getValue()
        
        variable = self.processor.frameModel.getVariable(self.operands[0].getFrameName())
        if self.__areOperandTypesOk():
            variable.set(str1 + str2, 'string')
        else:
            raise InterpretException("Invalid operand types", ReturnCodes.BAD_OPERANDS)
    
    def __areOperandTypesOk(self):
        return self.operands[1].getType() == 'string' and \
            self.operands[2].getType() == 'string'
    
class StrlenInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ VariableOperand, SymbolOperand ]
        super().__init__(operands, expectedOperands, processor)
        
    def execute(self): 
        string = self.operands[1].getValue()
        
        variable = self.processor.frameModel.getVariable(self.operands[0].getFrameName())
        if self.__isOperandTypeOk():
            variable.set(len(string), 'int')
        else:
            raise InterpretException("Invalid operand types", ReturnCodes.BAD_OPERANDS)
            
    def __isOperandTypeOk(self):
        return self.operands[1].getType() == 'string'
    
class GetcharInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ VariableOperand, SymbolOperand, SymbolOperand ]
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):  
        string = self.operands[1].getValue()
        index = self.operands[2].getValue() 
        
        variable = self.processor.frameModel.getVariable(self.operands[0].getFrameName())
        if self.operands[2].getType() == 'int' and self.operands[1].getType() == 'string':
            if index < 0 or index >= len(string):
                raise InterpretException("Invalid operand types", ReturnCodes.INVALID_STRING_OPERATION)
            variable.set(string[index], 'string')
        else:
            raise InterpretException("Invalid operand types", ReturnCodes.BAD_OPERANDS)
    
class SetcharInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ VariableOperand, SymbolOperand, SymbolOperand ]
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):  
        string = self.operands[0].getValue()
        index = self.operands[1].getValue()
        sourceString = self.operands[2].getValue()
           
        variable = self.processor.frameModel.getVariable(self.operands[0].getFrameName())
        if self.operands[0].getType() == 'string' and \
           self.operands[1].getType() == 'int' and \
           self.operands[2].getType() == 'string':
            if index < 0 or index >= len(string) or len(sourceString) == 0:
                raise InterpretException("Invalid operand types", ReturnCodes.INVALID_STRING_OPERATION)
            mutableString = list(string)
            mutableString[index] = sourceString[0]     
            variable.set("".join(mutableString), 'string')
        else:
            raise InterpretException("Invalid operand types", ReturnCodes.BAD_OPERANDS)

class Int2charInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ VariableOperand, SymbolOperand ]
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):  
        ordinal = self.operands[1].getValue()
            
        variable = self.processor.frameModel.getVariable(self.operands[0].getFrameName())
        if self.operands[1].getType() == 'int':
            try:
                char = chr(ordinal)
            except ValueError:
                raise InterpretException("Invalid operand types", ReturnCodes.INVALID_STRING_OPERATION)
            variable.set(char, 'string')
        else:
            raise InterpretException("Invalid operand types", ReturnCodes.BAD_OPERANDS)

class Stri2intInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ VariableOperand, SymbolOperand, SymbolOperand ]
        super().__init__(operands, expectedOperands, processor)
        
    def execute(self):  
        string = self.operands[1].getValue()
        index = self.operands[2].getValue()
        
        variable = self.processor.frameModel.getVariable(self.operands[0].getFrameName())
        if self.operands[1].getType() == 'string' and self.operands[2].getType() == 'int':
            if index < 0 or index >= len(string):
                raise InterpretException("Invalid operand types", ReturnCodes.INVALID_STRING_OPERATION)
            ordinal = ord(string[index])
            variable.set(ordinal, 'int')
        else:
            raise InterpretException("Invalid operand types", ReturnCodes.BAD_OPERANDS)

class DprintInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ SymbolOperand ]
        super().__init__(operands, expectedOperands, processor)
        
    def execute(self):
        print(self.operands[0].getValue(), file=sys.error) # todo

class ArithmeticInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ VariableOperand, SymbolOperand, SymbolOperand ]
        super().__init__(operands, expectedOperands, processor)
        
    def execute(self):
        if self.operands[1].getType() == None or self.operands[2].getType() == None:
            raise InterpretException("Missing value in operand", ReturnCodes.MISSING_VALUE)
        if self.operands[1].getType() != 'int' or self.operands[2].getType() != 'int':
            raise InterpretException("Invalid operand types", ReturnCodes.BAD_OPERANDS)

class AddInstruction(ArithmeticInstruction):
    
    def __init__(self, operands, processor):
        super().__init__(operands, processor)
        
    def execute(self):
        super().execute()
        val1 = self.operands[1].getValue()
        val2 = self.operands[2].getValue()
        
        variable = self.processor.frameModel.getVariable(self.operands[0].getFrameName())
        variable.set(val1 + val2, 'int')
        
class SubInstruction(ArithmeticInstruction):
    
    def __init__(self, operands, processor):
        super().__init__(operands, processor)
        
    def execute(self):
        super().execute()
        val1 = self.operands[1].getValue()
        val2 = self.operands[2].getValue()
        
        variable = self.processor.frameModel.getVariable(self.operands[0].getFrameName())
        variable.set(val1 - val2, 'int')        
        
class MulInstruction(ArithmeticInstruction):
    
    def __init__(self, operands, processor):
        super().__init__(operands, processor)
        
    def execute(self):
        super().execute()
        variable = self.processor.frameModel.getVariable(self.operands[0].getFrameName())
        val1 = self.operands[1].getValue()
        val2 = self.operands[2].getValue()
        variable.set(val1 * val2, 'int')    
        
class IdivInstruction(ArithmeticInstruction):
    
    def __init__(self, operands, processor):
        super().__init__(operands, processor)
        
    def execute(self):
        super().execute()
        val1 = self.operands[1].getValue()
        val2 = self.operands[2].getValue()
        if val2 == 0:
            raise InterpretException("Cannot divide by 0", ReturnCodes.BAD_OPERAND_VALUE)
            
        variable = self.processor.frameModel.getVariable(self.operands[0].getFrameName())
        variable.set(val1 // val2, 'int')    

class PushsInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ SymbolOperand ]
        super().__init__(operands, expectedOperands, processor)
        
    def execute(self):        
        value = self.operands[0].getValue()
        type = self.operands[0].getType()
        self.processor.pushToStack((value, type))
        
class PopsInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ SymbolOperand ]
        super().__init__(operands, expectedOperands, processor)
        
    def execute(self):        
        variable = self.processor.frameModel.getVariable(self.operands[0].getFrameName())
        value, type = self.processor.popFromStack()
        variable.set(value, type)

class RelationalInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ VariableOperand, SymbolOperand, SymbolOperand ]
        super().__init__(operands, expectedOperands, processor)
        
    def execute(self): 
        type1 = self.operands[1].getType()
        type2 = self.operands[2].getType()
        
        if type1 == None or type2 == None:
            raise InterpretException("Missing value in operand", ReturnCodes.MISSING_VALUE)
        if type1 == 'nil' or type2 == 'nil':
            return
        if type1 == type2:
            return
        raise InterpretException("Invalid operand types", ReturnCodes.BAD_OPERANDS)
    
class LtInstruction(RelationalInstruction):
    
    def __init__(self, operands, processor):
        super().__init__(operands, processor)
        
    def execute(self): 
        super().execute()
        value1 = self.operands[1].getValue()
        value2 = self.operands[2].getValue()
        
        if self.operands[1].getType() == 'nil' or self.operands[2].getType() == 'nil':
            raise InterpretException("Invalid operand types", ReturnCodes.BAD_OPERANDS)
        
        variable = self.processor.frameModel.getVariable(self.operands[0].getFrameName())
        variable.set(value1 < value2, 'bool')
    
class GtInstruction(RelationalInstruction):
    
    def __init__(self, operands, processor):
        super().__init__(operands, processor)
        
    def execute(self): 
        super().execute()
        value1 = self.operands[1].getValue()
        value2 = self.operands[2].getValue()
        
        if self.operands[1].getType() == 'nil' or self.operands[2].getType() == 'nil':
            raise InterpretException("Invalid operand types", ReturnCodes.BAD_OPERANDS)
            
        variable = self.processor.frameModel.getVariable(self.operands[0].getFrameName())
        variable.set(value1 > value2, 'bool')
        
class EqInstruction(RelationalInstruction):
    
    def __init__(self, operands, processor):
        super().__init__(operands, processor)
        
    def execute(self): 
        super().execute()
        variable = self.processor.frameModel.getVariable(self.operands[0].getFrameName())
        value1 = self.operands[1].getValue()
        value2 = self.operands[2].getValue()
        variable.set(value1 == value2, 'bool')
        
class AndInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ VariableOperand, SymbolOperand, SymbolOperand ]
        super().__init__(operands, expectedOperands, processor)
        
    def execute(self):
        value1 = self.operands[1].getValue()
        value2 = self.operands[2].getValue()
        
        if self.operands[1].getType() != 'bool' or self.operands[2].getType() != 'bool':
            raise InterpretException("Invalid operand types", ReturnCodes.BAD_OPERANDS)
            
        variable = self.processor.frameModel.getVariable(self.operands[0].getFrameName())
        variable.set(value1 and value2, 'bool')

class OrInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ VariableOperand, SymbolOperand, SymbolOperand ]
        super().__init__(operands, expectedOperands, processor)
        
    def execute(self):
        value1 = self.operands[1].getValue()
        value2 = self.operands[2].getValue()
        
        if self.operands[1].getType() != 'bool' or self.operands[2].getType() != 'bool':
            raise InterpretException("Invalid operand types", ReturnCodes.BAD_OPERANDS)
            
        variable = self.processor.frameModel.getVariable(self.operands[0].getFrameName())
        variable.set(value1 or value2, 'bool')
        
class NotInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ VariableOperand, SymbolOperand ]
        super().__init__(operands, expectedOperands, processor)
        
    def execute(self):
        value1 = self.operands[1].getValue()
        
        if self.operands[1].getType() != 'bool':
            raise InterpretException("Invalid operand types", ReturnCodes.BAD_OPERANDS)
        
        variable = self.processor.frameModel.getVariable(self.operands[0].getFrameName())
        variable.set(not value1, 'bool')
        
class DprintInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ SymbolOperand ]
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        sourceOperand = self.operands[0]
        self.__writeValue(sourceOperand.getValue(), sourceOperand.getType())
        
    def __writeValue(self, value, type):
        if type == 'bool':
            print('true' if value else 'false', file=sys.stderr)
        elif type == 'nil':
            print('', file=sys.stderr)
        elif type == 'int' or type == 'string':
            print(value, file=sys.stderr)
        else:
            raise InterpretException("Invalid argument type", ReturnCodes.INVALID_INPUT)

class BreakInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = []
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        print('Just some string', file=sys.stderr)
        
         
class Processor:
    
    def __init__(self, frameModel, operandFactory, inputFile):
        self.frameModel = frameModel
        self.__operandFactory = operandFactory
        self.__inputFile = inputFile
        self.instructionCounter = InstructionCounter()
        self.stopCode = None
        self.__dataStack = []
        
    def execute(self, rawInstructions):
        self.__createInstructions(rawInstructions)
        self.instructionCounter.setInstructions(self.instructions)
    
        while self.instructionCounter.nextInstruction() and self.stopCode == None:
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
            raise InterpretException(F"Unknown opcode {opcode}", ReturnCodes.INVALID_INPUT)
    
    def __createOperands(self, rawOperands):
        operands = []
        for rawOperand in rawOperands:
            operand = self.__operandFactory.create(rawOperand)
            operands.append(operand)
        return operands
            
    def stop(self, code):
        self.stopCode = code;
        
    def pushToStack(self, valueType):
        self.__dataStack.append(valueType)
    
    def popFromStack(self):
        if len(self.__dataStack) == 0:
            raise InterpretException('Empty data stack', ReturnCodes.MISSING_VALUE)
        return self.__dataStack.pop()

    def getInputFile(self):
        return self.__inputFile
 
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
        #print(self.currentInstruction, file=sys.stderr)
        self.currentInstruction.execute()
    
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
    
        
    
    
    