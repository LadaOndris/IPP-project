
from .frame import *
from .variable import *

class FrameModel:
    def __init__(self):
        self.globalFrame = Frame()
        self.localFrameStack = []
        self.temporaryFrame = None
      
    """
    Expects a parameter such as GF@var
    """
    def getVariable(self, variableFrameName):
        frameName, variableIdentifier = self.__parseVariableName(variableFrameName)
        frame = self.__getFrame(frameName)
        return frame.getVariable(variableIdentifier)
    
    def __parseVariableName(self, variable):
        return variable.split('@', 1)
        
    def __getFrame(self, frameName):
        if frameName == "GF":
            return self.globalFrame
        elif frameName == "LF":
            return self.localFrameStack[0]
        elif frameName == "TF":
            return self.temporaryFrame
        else:
            raise InterpretException("Unknown frame", ReturnCodes.INVALID_FRAME)
    
    def defvar(self, variableFrameName):
        frameName, variableIdentifier = self.__parseVariableName(variableFrameName)
        frame = self.__getFrame(frameName)
        variable = FrameVariable(variableIdentifier)
        frame.addVariable(variable)
        
    def resetTemporaryFrame():
        self.temporaryFrame = Frame()
    
    def pushTempFrameToLocalFrameStack():
        self.localFrameStack.push(self.temporaryFrame)
    
    def popFromLocalFrameStackToTempFrame():
        if len(self.localFrameStack) == 0:
            raise InterpretException('Empty frame stack', ReturnCodes.INVALID_FRAME)
        self.temporaryFrame = self.localFrameStack.pop()