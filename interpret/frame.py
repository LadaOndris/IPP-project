
from .return_codes import *

"""
The Frame class represents a container for a frame.
The frame contains variables that can be worked with.
"""
class Frame:
    def __init__(self):
        self.variables = {}
    
    """
    Adds a new variable to the frame.
    Raises an exception if the frame contains a variable with the same name. 
    """
    def addVariable(self, variable):
        if variable.name in self.variables:
            raise InterpretException("Redefinition of variable", ReturnCodes.SEMANTIC_ERROR)
        self.variables[variable.name] = variable
    
    """
    Gets a variable by it's name. 
    Raises an exception if the variable is not in the frame.
    """
    def getVariable(self, variableIdentifier):
        if variableIdentifier in self.variables:
            return self.variables[variableIdentifier]
        else:
            raise InterpretException(F"Unknown variable: {variableIdentifier}", \
                                     ReturnCodes.UKNOWN_VARIABLE)
