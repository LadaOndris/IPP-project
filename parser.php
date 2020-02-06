
<?php

interface IInputParser
{
    // returns Program
    public function parse();
}

interface IInstructionParser
{
    // returns Instruction
    public function getNextInstruction();
}

interface IInputReader
{
    public function readNextLine();
}

interface IProgramSerializer
{
    public function serialize($program);
}

class Main
{
    public function __construct() {
        $reader = new StdinInputReader();
        $instParser = new InstructionParser($reader);
        $inputParser = new InputParser($instParser);

        $serializer = new XmlProgramSerializer();
        
        $inputHeader = $reader->readNextLine();
        if ($this->isHeaderValid($inputHeader) == false) {
            return 21;
        }
        $program = $inputParser->parse();
        $serializer->serialize($program);

    }

    private function isHeaderValid($header) {
        return true; // todo
    }
}

class StdinInputReader implements IInputReader 
{
    public function readNextLine() {
        return "MOVE GF@counter string@";
    }
}

class InstructionParser implements IInstructionParser
{
    private $opcodes = ["DEFVAR", ""];
    private $reader;


    private $expectedOperandsList = array(
        "MOVE" => array(ArgType::VAR, ArgType::VAR),
        "CREATEFRAME" => array(),
        "PUSHFRAME" => array(),
        "POPFRAME" => array(),
        "DEFVAR" => array(ArgType::VAR),
        "CALL" => array(ArgType::LABEL),
        "RETURN" => array(),
        "PUSHS" => array(ArgType::VAR),
        "POPS" => array(ArgType::VAR),
    );

    public function __construct($reader) {
        $this->reader = $reader;
    }

    public function getNextInstruction() {
        // read line and reformat
        $line = $this->reader->readNextLine();
        $parts = explode(" ", $line);

        if (count($parts) <= 0) {
            return; // todo, error code
        }  
        $parts[0] = strtoupper($parts[0]);

        // todo, exists such opcode?
        $expectedOperands = $this->expectedOperandsList[$parts[0]];
        if ($this->actualEqualsExpected($parts, $expectedOperands) == false) {
            return; // todo, error code
        }
        $this->createInstruction($parts);
    }

    private function createInstruction($parts) {
        $opcode = $parts[0];
        $args = $this->parseArgs($parts);

        $inst = new Instruction($opcode, $args);
    }

    private function parseArgs($parts) {
        
    }

    private function actualEqualsExpected($actualLineParts, $expectedOperands) {
        if (count($actualLineParts) - 1 != count($expectedOperands)) {
            error_log("Wrong number of operands for instruction: " + $actualLineParts[0]);
            return false; // todo, error code
        }

        for ($i = 1; $i <= count($actualLineParts); $i++) {
            $isValid = ArgType::isArgValid($expectedOperands[$i - 1], $actualLineParts[$i]);
            if ($isValid == false) {
                return false; // todo, error code
            }
        }
        return true;
    }
}

class InputParser implements IInputParser
{
    private $instParser;

    public function __construct($instParser) {
        $this->instParser = $instParser;
    }

    public function parse() {
        return new Program();
    }
}

class Program
{
    private $instructions, $language;
}

class Instruction
{
    private $args, $opcode;
}

class Arg
{
    private $type, $content;
}

class ArgType
{
    public static const INT = "int";
    public static const BOOL = "bool"; // string, nil, label, type, var
    public static const STRING = "string";
    public static const NIL = "nil";
    public static const LABEL = "label";
    public static const TYPE = "type";
    public static const VAR = "var";

    public static function isArgValid($expectedArgType, $arg) {
        return true; // todo
    }
}

class XmlProgramSerializer implements IProgramSerializer
{
    public function serialize($program) {
        echo "program serialization";
    }
}


new Main();

?>