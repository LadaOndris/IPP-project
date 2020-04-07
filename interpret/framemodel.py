  
from .frame import *
from .variable import *

class FrameModel:
    
    """
    Initializes a new instance of the FrameModel class.
    Creates new global frame and empty list of local frames.
    """
    def __init__(self):
        self.globalFrame = Frame()
        self.localFrameStack = []
        self.temporaryFrame = None
        self.maximumVariables = 0
      
    """
    Returns a variable from the frame by its frame and variable name.
    variableFrameName defines the target frame and variable 
        in format such as GF@var
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
            frame = self.localFrameStack[-1]
        elif frameName == "TF":
            frame = self.temporaryFrame
        else:
            raise InterpretException("Unknown frame", ReturnCodes.INVALID_FRAME)
            
        if not isinstance(frame, Frame):
            raise InterpretException("Frame unavailable", ReturnCodes.INVALID_FRAME)
        return frame
    
    """
    Creates a new variable in the specified frame.
    """
    def defvar(self, variableFrameName):
        frameName, variableIdentifier = self.__parseVariableName(variableFrameName)
        frame = self.__getFrame(frameName)
        variable = FrameVariable(variableIdentifier)
        frame.addVariable(variable)
    
    """
    Creates new temporary frame.
    """
    def resetTemporaryFrame(self):
        self.temporaryFrame = Frame()
    
    """
    Takes the temporary frame and pushes it to the local frame stack.
    """
    def pushTempFrameToLocalFrameStack(self):
        if not isinstance(self.temporaryFrame, Frame):
            raise InterpretException("Temporary frame undefined", ReturnCodes.INVALID_FRAME)
        self.localFrameStack.append(self.temporaryFrame)
        self.temporaryFrame = None
    
    """ 
    Pops a frame from the local frame stack and 
    sets it as a temporary frame.
    """
    def popFromLocalFrameStackToTempFrame(self):
        if len(self.localFrameStack) == 0:
            raise InterpretException('Empty frame stack', ReturnCodes.INVALID_FRAME)
        self.temporaryFrame = self.localFrameStack.pop()
        
    """
    Counts current variables which exist in all frames.
    If the number of variables is higher than ever before, saves the count.
    """
    def updateMaximumVariables(self):
        variablesCount = self.countInitializedVariables(self.globalFrame)
        variablesCount += self.countInitializedVariables(self.temporaryFrame)
        for localFrame in self.localFrameStack:
            variablesCount += self.countInitializedVariables(localFrame)
            
        if self.maximumVariables < variablesCount:
            self.maximumVariables = variablesCount
    
    """
    Counts variables in specified frame.
    Doesn't count variables without value.
    """
    def countInitializedVariables(self, frame):
        count = 0
        if not isinstance(frame, Frame):
            return count
        for variable in frame.variables.values():
            if variable.isInitialized():
                count += 1
        return count
        
        
        
        
        
        