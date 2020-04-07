
"""
The FrameVariable represents a variable to be stored in a frame.
It has a name, value and type.
"""
class FrameVariable:
    
    def __init__(self, name):
        self.name = name
        self.value = None
        self.type = None
    
    """
    Sets the variable value and type.
    """
    def set(self, value, type):
        self.value = value
        self.type = type
        
    """
    Returns true if the value and type is not None.
    """
    def isInitialized(self):
        return not(self.value == None and type == None)