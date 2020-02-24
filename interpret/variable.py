

class Variable:
    
    def __init__(self, name, frame, value = None, type = None):
        self.name = name
        self.frame = frame
        self.value = value
        self.type = type
        
    def set(self, value, type):
        self.value = value
        self.type = type