from .return_codes import *
import re

"""
OperandFactory creates an instance of an appropriate 
argument class from a raw argument.
"""
class OperandFactory:
    
    def __init__(self, frameModel):
        self.__frameModel = frameModel
    
    """
    Creates an instance of an appropriate argument class 
    from a raw argument. Also casts the argument value based
    on its type. 
    Raises an exception if the cast fails.
    """
    def create(self, rawOperand):
        operandType = rawOperand.type
        operandValue = rawOperand.value
        
        if operandType == 'type':
            return TypeOperand(operandValue)
        elif operandType == 'label':
            return LabelOperand(operandValue)
        elif operandType == 'var':
            return VariableOperand(operandValue, self.__frameModel)
        elif operandType == 'nil':
            operandValue = self.__cast(operandValue, operandType)
            return ConstantOperand(operandValue, operandType)
        elif operandType == 'int':
            operandValue = self.__cast(operandValue, operandType)
            return ConstantOperand(operandValue, operandType)
        elif operandType == 'float':
            operandValue = self.__cast(operandValue, operandType)
            return ConstantOperand(operandValue, operandType)
        elif operandType == 'string':
            operandValue = self.__cast(operandValue, operandType)
            return ConstantOperand(operandValue, operandType)
        elif operandType == 'bool':
            operandValue = self.__cast(operandValue, operandType)
            return ConstantOperand(operandValue, operandType)
        else:
            raise InterpretException("Invalid operand", ReturnCodes.INVALID_INPUT)
    
    """
    Casts the given stringValue to the expected type.
    Type is a string selecting the type ('int', 'bool', 'nil', etc). 
    Raises an exception if the cast fails.
    """
    def __cast(self, stringValue, type):
        if type == 'bool':
            if stringValue.lower() == 'true':
                return True
            elif stringValue.lower() == 'false':
                return False
            else:
                raise InterpretException("Invalid boolean value", ReturnCodes.INVALID_INPUT)
        elif type == 'nil':
            return None
        elif type == 'int':
            try:
                return int(stringValue)
            except:
                raise InterpretException("Invalid int", ReturnCodes.INVALID_INPUT)
        elif type == 'float':
            try:
                return float.fromhex(stringValue)
            except:
                raise InterpretException("Invalid int", ReturnCodes.INVALID_INPUT)
        elif type == 'string':
            return self.__replaceChars(stringValue)
        else:
            raise InterpretException("Invalid operand type", ReturnCodes.INVALID_INPUT)
   
    """
    Replaced the ascii sequences in a encoded string
    to its true representations.
    For example '\097' is replaced by 'a'.
    """
    def __replaceChars(self, string):
        return re.sub(r'\\[0-9]{3}', self.convertToChar, string)
    
    """
    For the given regex sequence takes the first group 
    and returns its character value.
    
    For example for '\097' is return a letter 'a'.
    """
    def convertToChar(self, sequence):
        asciiChar = int(sequence.group(0)[1:])
        return chr(asciiChar)
        
"""
Base operand class.
Declares an abstract getValue method.
"""
class Operand:

    def __init__(self):
        pass     
    
    def getValue(self):
        raise NotImplementedError('Abstract method')
    
"""
Operand subclass representing a label as an operand.
"""
class LabelOperand(Operand):
    
    def __init__(self, value):
        self.__value = value
    
    def getValue(self):
        return self.__value
    
"""
Type subclass representing a type as an operand.
"""
class TypeOperand(Operand):
    
    def __init__(self, value):
        self.__value = value

    def getValue(self):
        return self.__value
    
"""
Symbol subclass representing a constant or variable as an operand.
"""
class SymbolOperand(Operand):

    def __init__(self):
        pass     
    
    """
    Returns type of the symbol.
    """
    def getType(self):
        raise NotImplementedError('Abstract method')

"""
Operand subclass representing a constant as an operand.
"""
class ConstantOperand(SymbolOperand):

    def __init__(self, value, type):
        self.__value = value
        self.__type = type

    """
    Returns value of the constant.
    """
    def getValue(self):
        return self.__value  
    
    """
    Returns type of the constant.
    """
    def getType(self):
        return self.__type

"""
Operand subclass representing a variable as an operand.
"""
class VariableOperand(SymbolOperand):

    def __init__(self, variableFrameName, frameModel):
        self.__frameModel = frameModel
        self.__variableFrameName = variableFrameName
        pass     
    
    """
    Returns value of the variable.
    """
    def getValue(self):
        variable = self.__frameModel.getVariable(self.__variableFrameName)
        if self.getType() == None:
            raise InterpretException("Missing value in operand", ReturnCodes.MISSING_VALUE)
        return variable.value  
    
    """
    Returns type of the variable.
    """
    def getType(self):
        variable = self.__frameModel.getVariable(self.__variableFrameName)
        return variable.type
    
    
    """
    Returns the variables name with its frame, 
    e.g. GF@var
    """
    def getFrameName(self):
        return self.__variableFrameName
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
