
from .frame import Frame
from .variable import Variable

class FrameModel:
    def __init__(self):
        self.globalFrame = Frame()
        self.localFrameStack = []
        self.temporaryFrame = None
      
    """
    Expects a parameter such as GF@var
    """
    def getVariable(self, variable):
        frameName, variableIdentifier = self.__parseVariableName(variable)
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
            raise Exception("Unknown frame")
    
    def defvar(self, argument):
        frameName, variableIdentifier = self.__parseVariableName(argument.value)
        frame = self.__getFrame(frameName)
        variable = Variable(variableIdentifier, frameName)
        frame.addVariable(variable)
        
    def resetTemporaryFrame():
        self.temporaryFrame = Frame()
    
    def pushTempFrameToLocalFrameStack():
        self.localFrameStack.append(self.temporaryFrame)
    
    def popFromLocalFrameStackToTempFrame():
        self.temporaryFrame = self.localFrameStack.pop()