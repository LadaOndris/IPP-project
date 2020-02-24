
class Instruction:
    
    def __init__(self, operands, expectedOperands, processor):
        self.operands = operands
        self.expectedOperands = expectedOperands
        self.processor = processor
        self.__checkOperands()
        
    def __checkOperands(self):
        if len(self.operands) != len(self.expectedOperands):
            raise Exception("Operands don't match")
        
    def getArgumentValueAndType(self, argument):
        if argument.type == 'var':
            variable = self.processor.frameModel.getVariable(argument.value)
            return variable.value, variable.type
        else:
            return argument.value, argument.type
            
    def execute(self):
        pass
    
class DefvarInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = ['var']
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        self.processor.frameModel.defvar(self.operands[0])

class MoveInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = ['var', 'symb']
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):        
        destinationOperand = self.operands[0]
        sourceOperand = self.operands[1]
        value, type = self.__getArgumentValueAndType(sourceOperand)
        variable = self.processor.frameModel.getVariable(destinationOperand.value)
        variable.set(value, type)
    
class WriteInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = ['symb']
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        sourceOperand = self.operands[0]
        value, type = self.getArgumentValueAndType(sourceOperand)
        self.__writeValue(value, type)
        
    def __writeValue(self, value, type):
        if type == 'bool':
            print('true' if value else 'false', end='')
        elif type == 'nil':
            print('', end='')
        elif type == 'int' or type == 'string':
            print(value, end='')
        else:
            raise Exception("Invalid argument type")
            
class ReadInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = ['symb', 'type']
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        toOperand = self.operands[0]
        typeOperand = self.operands[1]
        variable = self.processor.frameModel.getVariable(toOperand.value)
        value = self.__readValue(typeOperand.value)
        variable.set(value, typeOperand.value)
    
    def __readValue(self, type):
        value = input()
        return self.__convertToType(value, type)
        
    def __convertToType(self, value, type):
        if type == 'int':
            return int(value)
        if type == 'bool':
            return value.lower() == 'true'
        if type == 'string':
            return value
        raise Exception("Invalid type: " + type)

class CreateframeInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = []
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        self.processor.frameModel.resetTemporaryFrame()
    
class PushframeInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = []
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        self.processor.frameModel.pushTempFrameToLocalFrameStack()

class PopframeInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = []
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        self.processor.frameModel.popFromLocalFrameStackToTempFrame()
    
class CallInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = ['label']
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        self.processor.instructionCounter.pushCallstack()
        self.processor.instructionCounter.jumpTo(self.operands[0].value)
   
class ReturnInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = []
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        self.processor.instructionCounter.popCallstack()
        
class LabelInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = ['label']
        Instruction.__init__(self, operands, expectedOperands, processor)
        
class JumpInstruction(Instruction):
    
    def __init__(self, operands, processor):
        expectedOperands = ['label']
        Instruction.__init__(self, operands, expectedOperands, processor)
        
    def execute(self):
        self.processor.instructionCounter.jumpTo(self.operands[0].value)
    
    
class Processor:
    
    def __init__(self, frameModel):
        self.frameModel = frameModel
        self.instructionCounter = InstructionCounter()
        
    def execute(self, rawInstructions):
        self.__createInstructions(rawInstructions)
        self.instructionCounter.setInstructions(self.instructions)
    
        while self.instructionCounter.nextInstruction():
            self.instructionCounter.executeCurrentInstruction()
        
    def __createInstructions(self, rawInstructions):
        self.instructions = []
        for rawInstr in rawInstructions: 
            instruction = self.__createInstruction(rawInstr.opcode, rawInstr.arguments)
            self.instructions.append(instruction)
        
    def __createInstruction(self, opcode, operands):
        className = opcode.capitalize() + "Instruction"
        try:
            return eval(className)(operands, self)
        except NameError:
            raise Exception('Unknown opcode')
 
class InstructionCounter:
    
    def __init__(self):
        self.__counter = 0
        self.callStack = []
        
    def setInstructions(self, instructions):
        self.__counter = 0
        self.instructions = instructions
        self.__findLabels()
    
    def __findLabels(self):
        labels = {}
        for index, instr in enumerate(self.instructions):
            if isinstance(instr, LabelInstruction):
                label = instr.operands[0].value
                if label in labels:
                    raise Exception('Label already exists')
                labels[label] = index
        self.labels = labels
                        
    def nextInstruction(self):
        if self.__counter < len(self.instructions):
            self.currentInstruction = self.instructions[self.__counter]
            self.__incrementCounter()
            return True
        else:
            return False
    
    def executeCurrentInstruction(self):
        self.currentInstruction.execute()
    
    def __incrementCounter(self):
        self.__counter += 1
        
    def __decrementCounter(self):
        self.__counter -= 1
        
    def pushCallstack(self):
        self.callStack.append(self.__counter + 1)
    
    def popCallstack(self):
        if len(self.callStack) == 0:
            raise Exception('Callstack is empty', 56)
        self.__counter = self.callStack.pop()
        
    def jumpTo(self, label):
        if not label in self.labels:
            raise Exception('Label doesnt exist')
        self.__counter = self.labels[label] 
        
        
    
    
    