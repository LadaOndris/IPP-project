"""
This file contains all instructions which can be executed by processor.
All instructions inherit from Instruction class and implement an execute method.
Running instructions is designed as a Command design pattern.
To add new instruction, just add the new Instruction class with 
apropriate name and no further action is needed.

There is more complex hierarchy of instruction classes to avoid code duplication.

These instructions are executed by processor at the bottom of this file.
"""

from .operand import *
from .return_codes import *
import fileinput
import sys
import operator

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

class StackInstruction(Instruction):
    
    def __init__(self, operands, processor):
        super().__init__(operands, [], processor)


class UnaryStackInstruction(StackInstruction):
    
    def __init__(self, operands, processor, operation):
        super().__init__(operands, processor)
        self.operatorFunction = operation[0]
        self.allowedTypes = operation[1]
        self.resultType = operation[2]

    def execute(self):
        val, type = self.processor.popFromStack()
        self.checkType(type)
        
        result = self.operatorFunction(val)
        self.processor.pushToStack((result, self.resultType))
           
    def checkType(self, type):
        for allowedType in self.allowedTypes:
            if type == allowedType:
                return
        raise InterpretException("UNARY STACK ISNTR: Invalid operand types", ReturnCodes.BAD_OPERANDS)
        
class BinaryStackInstruction(StackInstruction):
    
    def __init__(self, operands, processor, operation, allowNils = False):
        super().__init__(operands, processor)
        self.operatorFunction = operation[0]
        self.allowedTypes = operation[1]
        self.resultType = operation[2]
        self.allowNils = allowNils

    def execute(self):
        val2, type2 = self.processor.popFromStack()
        val1, type1 = self.processor.popFromStack()
        
        self.checkTypes(type1, type2)
        
        result = self.operatorFunction(val1, val2)
        self.processor.pushToStack((result, self.resultType))
           
    def checkTypes(self, type1, type2):
        if (self.allowNils and (type1 == 'nil' or type2 == 'nil')):
            return
        for allowedType in self.allowedTypes:
            if type1 == allowedType and type2 == allowedType:
                return
        print(F"BINARY STACK INSTR: type1: {type1}, type2: {type2}", file=sys.stderr)
        raise InterpretException("BINARY STACK INSTR: Invalid operand types", ReturnCodes.BAD_OPERANDS)
        
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
        elif type == 'float':
            #print('float', file=sys.stderr)
            print(value.hex(), end='')
        elif type == 'int' or type == 'string':
            #print('int, string', file=sys.stderr)
            print(value, end='')
        else:
            raise InterpretException("WRITE: Invalid argument type", ReturnCodes.INVALID_INPUT)
            
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
        value = input()
        return self.__convertToType(value, type), type
        
    def __convertToType(self, value, type):
        if type == 'int':
            return int(value)
        if type == 'bool':
            return value.lower() == "true"
        if type == 'float':
            return float.fromhex(value)
        if type == 'string':
            return value
        raise InterpretException("READ: Invalid type: " + type, ReturnCodes.INVALID_INPUT)

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
            raise InterpretException('JUMPIFEQ: Types differ', ReturnCodes.BAD_OPERANDS)
        if val1 == val2:
            self.processor.instructionCounter.jumpTo(label)
    
class JumpifeqsInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ LabelOperand ]
        super().__init__(operands, expectedOperands, processor)
        
    def execute(self):
        val2, type2 = self.processor.popFromStack()
        val1, type1 =  self.processor.popFromStack()
        label = self.operands[0].getValue()
        
        if type1 != type2 and type1 != 'nil' and type2 != 'nil':
            raise InterpretException('JUMPIFEQS: Types differ', ReturnCodes.BAD_OPERANDS)
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
            raise InterpretException('JUMPIFNEQ: Types differ', ReturnCodes.BAD_OPERANDS)
        
        if val1 != val2:
            self.processor.instructionCounter.jumpTo(label)
    
class JumpifneqsInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ LabelOperand ]
        super().__init__(operands, expectedOperands, processor)
        
    def execute(self):
        val2, type2 = self.processor.popFromStack()
        val1, type1 =  self.processor.popFromStack()
        label = self.operands[0].getValue()
        
        if type1 != type2 and type1 != 'nil' and type2 != 'nil':
            raise InterpretException('JUMPIFNEQS: Types differ', ReturnCodes.BAD_OPERANDS)
        if val1 != val2:
            self.processor.instructionCounter.jumpTo(label)
            
class ExitInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ SymbolOperand ]
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        exitCode = self.operands[0].getValue()
        
        if self.operands[0].getType() != 'int':
            raise InterpretException('EXIT: Invalid exit code operand', ReturnCodes.BAD_OPERANDS)
            
        if exitCode >= 0 and exitCode <= 49:
            self.processor.stop(exitCode)
        else:
            raise InterpretException('EXIT: Invalid exit code', ReturnCodes.BAD_OPERAND_VALUE)

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
            raise InterpretException("CONCAT: Invalid operand types", ReturnCodes.BAD_OPERANDS)
    
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
            raise InterpretException("STRLEN: Invalid operand types", ReturnCodes.BAD_OPERANDS)
            
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
                raise InterpretException("GETCHAR: Invalid operand types", ReturnCodes.INVALID_STRING_OPERATION)
            variable.set(string[index], 'string')
        else:
            raise InterpretException("GETCHAR: Invalid operand types", ReturnCodes.BAD_OPERANDS)
    
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
                raise InterpretException("SETCHAR: Invalid operand types", ReturnCodes.INVALID_STRING_OPERATION)
            mutableString = list(string)
            mutableString[index] = sourceString[0]     
            variable.set("".join(mutableString), 'string')
        else:
            raise InterpretException("SETCHAR: Invalid operand types", ReturnCodes.BAD_OPERANDS)

class Int2charInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ VariableOperand, SymbolOperand ]
        super().__init__(operands, expectedOperands, processor)
        
    def execute(self):  
        ordinal = self.operands[1].getValue()
            
        variable = self.processor.frameModel.getVariable(self.operands[0].getFrameName())
        if self.operands[1].getType() == 'int':
            try:
                char = chr(ordinal)
            except ValueError:
                raise InterpretException("INT2CHAR: Invalid operand types", ReturnCodes.INVALID_STRING_OPERATION)
            variable.set(char, 'string')
        else:
            raise InterpretException("INT2CHAR: Invalid operand types", ReturnCodes.BAD_OPERANDS)


class Int2charsInstruction(StackInstruction):
    
    def __init__(self, operands, processor):
        super().__init__(operands, processor)
        
    def execute(self):  
        ordinal, ordinalType = self.processor.popFromStack()
           
        if ordinalType == 'int':
            try:
                char = chr(ordinal)
            except ValueError:
                raise InterpretException("INT2CHARS: Invalid operand types", ReturnCodes.INVALID_STRING_OPERATION)
            self.processor.pushToStack((char, 'string'))
        else:
            raise InterpretException("INT2CHARS: Invalid operand types", ReturnCodes.BAD_OPERANDS)

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
                raise InterpretException("STRI2INT: Invalid operand types", ReturnCodes.INVALID_STRING_OPERATION)
            ordinal = ord(string[index])
            variable.set(ordinal, 'int')
        else:
            raise InterpretException("STRI2INT: Invalid operand types", ReturnCodes.BAD_OPERANDS)

class Stri2intsInstruction(StackInstruction):
    
    def __init__(self, operands, processor):
        super().__init__(operands, processor)
        
    def execute(self):  
        index, indexType = self.processor.popFromStack()
        string, stringType = self.processor.popFromStack()
        
        if stringType == 'string' and indexType == 'int':
            if index < 0 or index >= len(string):
                raise InterpretException("STRI2INTS: Invalid operand types", ReturnCodes.INVALID_STRING_OPERATION)
            ordinal = ord(string[index])
            self.processor.pushToStack((ordinal, 'int'))
        else:
            raise InterpretException("STRI2INTS: Invalid operand types", ReturnCodes.BAD_OPERANDS)


class Int2floatInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ VariableOperand, SymbolOperand ]
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):  
        ordinal = self.operands[1].getValue()
            
        variable = self.processor.frameModel.getVariable(self.operands[0].getFrameName())
        if self.operands[1].getType() != 'int':
            raise InterpretException("INT2FLOAT: Invalid operand types", ReturnCodes.BAD_OPERANDS)
            
        variable.set(float(self.operands[1].getValue()), 'float')
        
class Int2floatsInstruction(StackInstruction):
    
    def __init__(self, operands, processor):
        super().__init__(operands, processor)
        
    def execute(self):
        ordinalVal, ordinalType = self.processor.popFromStack()
        
        if ordinalType != 'int':
            raise InterpretException("INT2FLOATS: Invalid operand types", ReturnCodes.BAD_OPERANDS)
        
        self.processor.pushToStack((float(ordinalVal), 'float'))

class Float2intInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ VariableOperand, SymbolOperand ]
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):  
        ordinal = self.operands[1].getValue()
            
        variable = self.processor.frameModel.getVariable(self.operands[0].getFrameName())
        if self.operands[1].getType() != 'float':
            raise InterpretException("FLOAT2INT: Invalid operand types", ReturnCodes.BAD_OPERANDS)
            
        variable.set(int(self.operands[1].getValue()), 'int')
        
class Float2intsInstruction(StackInstruction):
    
    def __init__(self, operands, processor):
        super().__init__(operands, processor)
        
    def execute(self):
        ordinalVal, ordinalType = self.processor.popFromStack()
        
        if ordinalType != 'float':
            raise InterpretException("FLOAT2INTS: Invalid operand types", ReturnCodes.BAD_OPERANDS)
        
        self.processor.pushToStack((int(ordinalVal), 'int'))

class ArithmeticInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ VariableOperand, SymbolOperand, SymbolOperand ]
        super().__init__(operands, expectedOperands, processor)
        
    def execute(self):
        type1 = self.operands[1].getType()
        type2 = self.operands[2].getType()
        if type1 == 'int' and type2 == 'int':
            return
        if type1 == 'float' and type2 == 'float':
            return
        if type1 == None or type2 == None:
            raise InterpretException("ARITHMETIC: Missing value in operand", ReturnCodes.MISSING_VALUE)
        raise InterpretException("ARITHMETIC: Invalid operand types", ReturnCodes.BAD_OPERANDS)

class AddInstruction(ArithmeticInstruction):
    
    def __init__(self, operands, processor):
        super().__init__(operands, processor)
        
    def execute(self):
        super().execute()
        val1 = self.operands[1].getValue()
        val2 = self.operands[2].getValue()
        
        variable = self.processor.frameModel.getVariable(self.operands[0].getFrameName())
        variable.set(val1 + val2, self.operands[1].getType())
        
class SubInstruction(ArithmeticInstruction):
    
    def __init__(self, operands, processor):
        super().__init__(operands, processor)
        
    def execute(self):
        super().execute()
        val1 = self.operands[1].getValue()
        val2 = self.operands[2].getValue()
        
        variable = self.processor.frameModel.getVariable(self.operands[0].getFrameName())
        variable.set(val1 - val2, self.operands[1].getType())        
        
class MulInstruction(ArithmeticInstruction):
    
    def __init__(self, operands, processor):
        super().__init__(operands, processor)
        
    def execute(self):
        super().execute()
        variable = self.processor.frameModel.getVariable(self.operands[0].getFrameName())
        val1 = self.operands[1].getValue()
        val2 = self.operands[2].getValue()
        variable.set(val1 * val2, self.operands[1].getType())    
        
class IdivInstruction(ArithmeticInstruction):
    
    def __init__(self, operands, processor):
        super().__init__(operands, processor)
        
    def execute(self):
        super().execute()
        val1 = self.operands[1].getValue()
        val2 = self.operands[2].getValue()
        if val2 == 0:
            raise InterpretException("IDIV: Cannot divide by 0", ReturnCodes.BAD_OPERAND_VALUE)
        
        if self.operands[1].getType() != 'int' or self.operands[2].getType() != 'int':
            raise InterpretException("IDIV: Invalid operand types", ReturnCodes.BAD_OPERANDS)
            
        variable = self.processor.frameModel.getVariable(self.operands[0].getFrameName())
        variable.set(val1 // val2, 'int')    
        
class DivInstruction(ArithmeticInstruction):
    
    def __init__(self, operands, processor):
        super().__init__(operands, processor)
        
    def execute(self):
        super().execute()
        val1 = self.operands[1].getValue()
        val2 = self.operands[2].getValue()
        if val2 == 0:
            raise InterpretException("DIV: Cannot divide by 0", ReturnCodes.BAD_OPERAND_VALUE)
            
        if self.operands[1].getType() != 'float' or self.operands[2].getType() != 'float':
            raise InterpretException("DIV: Invalid operand types", ReturnCodes.BAD_OPERANDS)
            
        variable = self.processor.frameModel.getVariable(self.operands[0].getFrameName())
        variable.set(val1 / val2, 'float')    

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
            raise InterpretException("Relational inst: Missing value in operand", ReturnCodes.MISSING_VALUE)
        if type1 == 'nil' or type2 == 'nil':
            return
        if type1 == type2:
            return
        raise InterpretException("Relational inst: Invalid operand types", ReturnCodes.BAD_OPERANDS)
    
class LtInstruction(RelationalInstruction):
    
    def __init__(self, operands, processor):
        super().__init__(operands, processor)
        
    def execute(self): 
        super().execute()
        value1 = self.operands[1].getValue()
        value2 = self.operands[2].getValue()
        
        if self.operands[1].getType() == 'nil' or self.operands[2].getType() == 'nil':
            raise InterpretException("LT: Invalid operand types", ReturnCodes.BAD_OPERANDS)
        
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
            raise InterpretException("GT: Invalid operand types", ReturnCodes.BAD_OPERANDS)
            
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
            raise InterpretException("AND: Invalid operand types", ReturnCodes.BAD_OPERANDS)
            
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
            raise InterpretException("OR: Invalid operand types", ReturnCodes.BAD_OPERANDS)
            
        variable = self.processor.frameModel.getVariable(self.operands[0].getFrameName())
        variable.set(value1 or value2, 'bool')
        
class NotInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ VariableOperand, SymbolOperand ]
        super().__init__(operands, expectedOperands, processor)
        
    def execute(self):
        value1 = self.operands[1].getValue()
        
        if self.operands[1].getType() != 'bool':
            raise InterpretException("NOT: Invalid operand types", ReturnCodes.BAD_OPERANDS)
        
        variable = self.processor.frameModel.getVariable(self.operands[0].getFrameName())
        variable.set(not value1, 'bool')
        
class DprintInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = [ SymbolOperand ]
        super().__init__(operands, expectedOperands, processor)
        
    def execute(self):
        sourceOperand = self.operands[0]
        self.__writeValue(sourceOperand.getValue(), sourceOperand.getType())
        
    def __writeValue(self, value, type):
        if type == 'bool':
            print('true' if value else 'false', file=sys.stderr)
        elif type == 'nil':
            print('', file=sys.stderr)
        elif type == 'float':
            print(value, file=sys.stderr)
        elif type == 'int' or type == 'string':
            print(value, file=sys.stderr)
        else:
            raise InterpretException("DPRINT: Invalid argument type", ReturnCodes.INVALID_INPUT)

class BreakInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = []
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        print('Just some string', file=sys.stderr)
        

class ClearsInstruction(Instruction):
    
    def __init__(self, operands, processor):
        super().__init__(operands, [], processor)     
        
    def execute(self):
        self.processor.clearStack()
        
class AddsInstruction(StackInstruction):
   
    def __init__(self, operands, processor):
        super().__init__(operands, processor)
        
    def execute(self):
        val2, type2 = self.processor.popFromStack()
        val1, type1 = self.processor.popFromStack()
        
        if (type1 != type2 or (type1 != 'int' and type2 != 'float')):
            raise InterpretException("ADDS: Invalid operand types", ReturnCodes.BAD_OPERANDS)
        
        self.processor.pushToStack((val1 + val2, type1))
        
class SubsInstruction(StackInstruction):
   
    def __init__(self, operands, processor):
        super().__init__(operands, processor)
        
    def execute(self):
        val2, type2 = self.processor.popFromStack()
        val1, type1 = self.processor.popFromStack()
        
        if (type1 != type2 or (type1 != 'int' and type2 != 'float')):
            raise InterpretException("SUBS: Invalid operand types", ReturnCodes.BAD_OPERANDS)
        
        self.processor.pushToStack((val1 - val2, type1))
         
class MulsInstruction(StackInstruction):
   
    def __init__(self, operands, processor):
        super().__init__(operands, processor)
        
    def execute(self):
        val2, type2 = self.processor.popFromStack()
        val1, type1 = self.processor.popFromStack()
        
        if (type1 != type2 or (type1 != 'int' and type2 != 'float')):
            raise InterpretException("MULS: Invalid operand types", ReturnCodes.BAD_OPERANDS)
        
        self.processor.pushToStack((val1 * val2, type1))

class IdivsInstruction(BinaryStackInstruction):
   
    def __init__(self, operands, processor):
        operation = (operator.floordiv, ['int'], 'int')
        super().__init__(operands, processor, operation)
        
    def execute(self):
        super().execute()
        
class DivsInstruction(BinaryStackInstruction):
   
    def __init__(self, operands, processor):
        operation = (operator.truediv, ['float'], 'float')
        super().__init__(operands, processor, operation)
        
    def execute(self):
        super().execute()
        
class AndsInstruction(BinaryStackInstruction):
   
    def __init__(self, operands, processor):
        operation = (operator.and_, ['bool'], 'bool')
        super().__init__(operands, processor, operation)
        
    def execute(self):
        super().execute()

class OrsInstruction(BinaryStackInstruction):
   
    def __init__(self, operands, processor):
        operation = (operator.or_, ['bool'], 'bool')
        super().__init__(operands, processor, operation)
        
    def execute(self):
        super().execute()

class GtsInstruction(BinaryStackInstruction):
   
    def __init__(self, operands, processor):
        operation = (operator.gt, ['int', 'bool', 'float', 'string'], 'bool')
        super().__init__(operands, processor, operation)
        
    def execute(self):
        super().execute()
        
class LtsInstruction(BinaryStackInstruction):
   
    def __init__(self, operands, processor):
        operation = (operator.lt, ['int', 'bool', 'float', 'string'], 'bool')
        super().__init__(operands, processor, operation)
        
    def execute(self):
        super().execute()
        
class EqsInstruction(BinaryStackInstruction):
   
    def __init__(self, operands, processor):
        operation = (operator.eq, ['int', 'bool', 'float', 'string', 'nil'], 'bool')
        super().__init__(operands, processor, operation, allowNils = True)
        
    def execute(self):
        super().execute()
        
class NotsInstruction(UnaryStackInstruction):
   
    def __init__(self, operands, processor):
        operation = (operator.not_, ['int', 'bool', 'float', 'string'], 'bool')
        super().__init__(operands, processor, operation)
        
    def execute(self):
        super().execute()
       
"""
The processor executes all instructions.
"""
class Processor:
    
    def __init__(self, frameModel, operandFactory, instructionCounter, inputFile):
        self.frameModel = frameModel
        self.__operandFactory = operandFactory
        self.__inputFile = inputFile
        self.instructionCounter = instructionCounter
        self.stopCode = None
        self.__dataStack = []
        
    """
    Execute all instructions.
    rawInstructions is a list of Instruction
    """
    def execute(self, rawInstructions):
        self.__createInstructions(rawInstructions)
        self.instructionCounter.setInstructions(self.instructions)
    
        while self.instructionCounter.nextInstruction() and self.stopCode == None:
            self.instructionCounter.executeCurrentInstruction()
            self.frameModel.updateMaximumVariables()
    
    """
    Create an instance of appropriate Instruction class 
    for every instruction.
    """
    def __createInstructions(self, rawInstructions):
        self.instructions = []
        for rawInstr in rawInstructions: 
            instruction = self.__createInstruction(rawInstr.opcode, rawInstr.arguments)
            self.instructions.append(instruction)
        
    """
    Create an instancen of appropriate Instruction class
    and return it.
    """
    def __createInstruction(self, opcode, rawOperands):
        operands = self.__createOperands(rawOperands)
        className = opcode.capitalize() + "Instruction"
        
        try:
            return eval(className)(operands, self)
        except NameError:
            raise InterpretException(F"Unknown opcode {opcode}", ReturnCodes.INVALID_INPUT)

    """
    Create an instance of appropriate Argument class 
    for every operand.
    """
    def __createOperands(self, rawOperands):
        operands = []
        for rawOperand in rawOperands:
            operand = self.__operandFactory.create(rawOperand)
            operands.append(operand)
        return operands
        
    """
    Instruction for the processor to stop with the specified code.
    """
    def stop(self, code):
        self.stopCode = code;
    
    """
    Appends a variable to the data stack.
    """
    def pushToStack(self, valueType):
        self.__dataStack.append(valueType)
    
    """
    Pops a variable from the data stack.
    """
    def popFromStack(self):
        if len(self.__dataStack) == 0:
            raise InterpretException('Empty data stack', ReturnCodes.MISSING_VALUE)
        return self.__dataStack.pop()

    """
    Clears the data stack.
    """
    def clearStack(self):
        self.__dataStack = []

    """
    Returns an input file.
    """
    def getInputFile(self):
        return self.__inputFile
 
        
    
    
    