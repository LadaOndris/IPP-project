
from .return_codes import *

class Frame:
    def __init__(self):
        self.variables = {}
    
    def addVariable(self, variable):
        self.variables[variable.name] = variable
        
    def getVariable(self, variableIdentifier):
        if variableIdentifier in self.variables:
            return self.variables[variableIdentifier]
        else:
            raise InterpretException(F"Unknown variable: {variableIdentifier}", \
                                     ReturnCodes.UKNOWN_VARIABLE)
