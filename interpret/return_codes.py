
class ReturnCodes:
    SUCCESS = 0
    SCRIPT_PARAMETER_ERROR = 10
    INPUT_FILE_ERROR = 11
    OUTPUT_FILE_ERROR = 12
    INVALID_XML_STRUCTURE = 31
    INVALID_INPUT = 32
    SEMANTIC_ERROR = 52
    BAD_OPERANDS = 53
    UKNOWN_VARIABLE = 54
    INVALID_FRAME = 55
    MISSING_VALUE = 56
    BAD_OPERAND_VALUE = 57
    INVALID_STRING_OPERATION = 58
    INTERNAL_ERROR = 99
    

class InterpretException(Exception):
    
    def __init__(self, message, code):
        super().__init__(message, code)
        