
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
            frame = self.globalFrame
        elif frameName == "LF":
            if len(self.localFrameStack) == 0:
                raise InterpretException("There is no local frame", ReturnCodes.INVALID_FRAME)
            frame = self.localFrameStack[0]
        elif frameName == "TF":
            frame = self.temporaryFrame
        else:
            raise InterpretException("Unknown frame", ReturnCodes.INVALID_FRAME)
            
        if not isinstance(frame, Frame):
            raise InterpretException("Frame unavailable", ReturnCodes.INVALID_FRAME)
        return frame
    
    def defvar(self, variableFrameName):
        frameName, variableIdentifier = self.__parseVariableName(variableFrameName)
        frame = self.__getFrame(frameName)
        variable = FrameVariable(variableIdentifier)
        frame.addVariable(variable)
        
    def resetTemporaryFrame(self):
        self.temporaryFrame = Frame()
    
    def pushTempFrameToLocalFrameStack(self):
        if not isinstance(self.temporaryFrame, Frame):
            raise InterpretException("Temporary frame undefined", ReturnCodes.INVALID_FRAME)
        self.localFrameStack.insert(0, self.temporaryFrame)
    
    def popFromLocalFrameStackToTempFrame(self):
        if len(self.localFrameStack) == 0:
            raise InterpretException('Empty frame stack', ReturnCodes.INVALID_FRAME)
        self.temporaryFrame = self.localFrameStack.pop()