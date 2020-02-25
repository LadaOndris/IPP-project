

class FrameVariable:
    
    def __init__(self, name):
        self.name = name
        self.value = None
        self.type = None
        
    def set(self, value, type):
        self.value = value
        self.type = type