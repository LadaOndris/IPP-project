
class OperandFactory:
    
    def __init__(self, frameModel):
        self.__frameModel = frameModel
    
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
        elif operandType == 'string':
            operandValue = self.__cast(operandValue, operandType)
            return ConstantOperand(operandValue, operandType)
        elif operandType == 'bool':
            operandValue = self.__cast(operandValue, operandType)
            return ConstantOperand(operandValue, operandType)
        else:
            raise Exception('Invalid operand')
    
    def __cast(self, stringValue, type):
        if type == 'bool':
            return bool(stringValue)
        elif type == 'nil':
            return None
        elif type == 'int':
            return int(stringValue)
        elif type == 'string':
            return stringValue
        else:
            raise Exception('Invalid type')
        
class Operand:

    def __init__(self):
        pass     
    
    def getValue(self):
        raise NotImplementedError('Abstract method')
    

class LabelOperand(Operand):
    
    def __init__(self, value):
        self.__value = value
    
    def getValue(self):
        return self.__value
    
class TypeOperand(Operand):
    
    def __init__(self, value):
        self.__value = value

    def getValue(self):
        return self.__value
    
class SymbolOperand(Operand):

    def __init__(self):
        pass     
    
    def getType(self):
        raise NotImplementedError('Abstract method')

class ConstantOperand(SymbolOperand):

    def __init__(self, value, type):
        self.__value = value
        self.__type = type

    def getValue(self):
        return self.__value  
    
    def getType(self):
        return self.__type

class VariableOperand(SymbolOperand):

    def __init__(self, variableFrameName, frameModel):
        self.__frameModel = frameModel
        self.__variableFrameName = variableFrameName
        pass     
    
    def getValue(self):
        variable = self.__frameModel.getVariable(self.__variableFrameName)
        return variable.value  
    
    def getType(self):
        variable = self.__frameModel.getVariable(self.__variableFrameName)
        return variable.type
    
    # return GF@a for instance
    def getFrameName(self):
        return self.__variableFrameName
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
