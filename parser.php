
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
        $this->reader = new StdinInputReader();
        $this->instParser = new InstructionParser($this->reader);
        $this->inputParser = new InputParser($this->instParser);
        $this->serializer = new XmlProgramSerializer();
    }

    public function begin() {
        $inputHeader = $this->reader->readNextLine();
        if ($this->isHeaderValid($inputHeader) == false) {
            return 21;
        }
        $parseResult = $this->inputParser->parse();
        if (is_numeric($parseResult)) {
            return $parseResult; 
        }
        $this->serializer->serialize($parseResult);
        return 0;
    }

    private function isHeaderValid($header) {
        return trim($header) == '.IPPcode20';
    }
}

class StdinInputReader implements IInputReader 
{
    public function readNextLine() {
        #return "MOVE GF@counter string@";
        $line = fgets(STDIN);
        return $line;
    }

}

class InstructionParser implements IInstructionParser
{
    private $reader;
    private $expectedOperandsList = array(
        "MOVE" => array(ArgType::VAR, ArgType::SYMB),
        "CREATEFRAME" => array(),
        "PUSHFRAME" => array(),
        "POPFRAME" => array(),
        "DEFVAR" => array(ArgType::VAR),
        "CALL" => array(ArgType::LABEL),
        "RETURN" => array(),

        "PUSHS" => array(ArgType::SYMB),
        "POPS" => array(ArgType::VAR),

        "ADD" => array(ArgType::VAR, ArgType::SYMB, ArgType::SYMB),
        "SUB" => array(ArgType::VAR, ArgType::SYMB, ArgType::SYMB),
        "MUL" => array(ArgType::VAR, ArgType::SYMB, ArgType::SYMB),
        "IDIV" => array(ArgType::VAR, ArgType::SYMB, ArgType::SYMB),
        "LT" => array(ArgType::VAR, ArgType::SYMB, ArgType::SYMB),
        "GT" => array(ArgType::VAR, ArgType::SYMB, ArgType::SYMB),
        "EQ" => array(ArgType::VAR, ArgType::SYMB, ArgType::SYMB),
        "AND" => array(ArgType::VAR, ArgType::SYMB, ArgType::SYMB),
        "OR" => array(ArgType::VAR, ArgType::SYMB, ArgType::SYMB),
        "NOT" => array(ArgType::VAR, ArgType::SYMB, ArgType::SYMB),
        "INT2CHAR" => array(ArgType::VAR, ArgType::SYMB),
        "STRI2INT" => array(ArgType::VAR, ArgType::SYMB, ArgType::SYMB),
        
        "READ" => array(ArgType::VAR, ArgType::TYPE),
        "WRITE" => array(ArgType::SYMB),

        "CONCAT" => array(ArgType::VAR, ArgType::SYMB, ArgType::SYMB),
        "STRLEN" => array(ArgType::VAR, ArgType::SYMB),
        "GETCHAR" => array(ArgType::VAR, ArgType::SYMB, ArgType::SYMB),
        "SETCHAR" => array(ArgType::VAR, ArgType::SYMB, ArgType::SYMB),
        "TYPE" => array(ArgType::VAR, ArgType::SYMB),

        "LABEL" => array(ArgType::LABEL),
        "JUMP" => array(ArgType::LABEL),
        "JUMPIFEQ" => array(ArgType::LABEL, ArgType::SYMB, ArgType::SYMB),
        "JUMPIFNEQ" => array(ArgType::LABEL, ArgType::SYMB, ArgType::SYMB),
        "EXIT" => array(ArgType::SYMB),

        "DPRINT" => array(ArgType::SYMB),
        "BREAK" => array(),
    );

    public function __construct($reader) {
        $this->reader = $reader;
    }

    public function getNextInstruction() {
        // read line and reformat
        $parts = $this->readNextNonEmptyLine();
        if ($parts === NULL) {
            return NULL;
        }
        $parts[0] = strtoupper($parts[0]);
        
        if (array_key_exists($parts[0], $this->expectedOperandsList) == false) {
            error_log("Invalid instruction: *" . $parts[0]."*");
            return 22;
        }
        $expectedOperands = $this->expectedOperandsList[$parts[0]];
        if ($this->actualEqualsExpected($parts, $expectedOperands) == false) {
            error_log("Expected operands don't match given.");
            return 23;
        }
        $instr = $this->createInstruction($parts, $expectedOperands);
        if (!($instr instanceof Instruction)) {
            return 23;
        }
        return $instr;
    }

    private function readNextNonEmptyLine() {
        do {
            $line = $this->reader->readNextLine();
            if (!$line) {
                return NULL;
            }
            
            $line = trim($line); // get rid of white spaces
            $line = explode("#", $line)[0]; // get rid of comments
            $parts = explode(" ", $line);
            $parts = array_filter($parts, function($s) {
                return $s !== "";
            });
        } while(count($parts) == 0);
        
        print_r($parts);
        return $parts;
    }

    private function createInstruction($parts, $expectedOperands) {
        $opcode = $parts[0];
        $args = $this->parseArgs($parts, $expectedOperands);
        if (is_numeric($args)) // is error
            return $args;
        $inst = new Instruction($opcode, $args);
        return $inst;
    }

    private function parseArgs($parts, $operandTypes) {
        $args = array();
        for ($i = 0; $i < count($operandTypes); $i++) {
            $operandType = $operandTypes[$i];
            $operand = $parts[$i + 1];

            switch ($operandType) {
                case ArgType::INT:
                case ArgType::BOOL:
                case ArgType::STRING: {
                    $content = $this->parseVal($operand);
                } break;
                case ArgType::TYPE:
                case ArgType::VAR: {
                    $content = $this->parseVar($operand);
                } break;
                case ArgType::LABEL:
                case ArgType::NIL: {
                    $content = $operand;
                } break;
                case ArgType::SYMB: {
                    if ($this->isVar($operand)) {
                        $operandType = ArgType::VAR;
                        $content = $operand;
                    }
                    elseif ($this->isString($operand)) {
                        $operandType = ArgType::STRING;
                        $content = $this->parseVal($operand);
                    }
                    elseif ($this->isInt($operand)) {
                        $operandType = ArgType::INT;
                        $content = $this->parseVal($operand);
                    }
                    elseif ($this->isBool($operand)) {
                        $operandType = ArgType::BOOL;
                        $content = $this->parseVal($operand);
                    }
                    elseif ($this->isNil($operand)) {
                        $operandType = ArgType::BOOL;
                        $content = $this->parseVal($operand);
                    }
                    else {
                        return 23; // error
                    }
                } break;
            }
            $arg = new Arg($operandType, $content);
            array_push($args, $arg);
        }
        return $args;
    }

    private function isVar($subject) {
        return preg_match("/^(GF|LF|TF)\@.+/", $subject);
    }

    private function isString($subject) {
        return preg_match("/^string\@.*/", $subject);
    }
    
    private function isInt($subject) {
        return preg_match("/^int\@.+/", $subject);
    }
    
    private function isBool($subject) {
        return preg_match("/^bool\@(true|false)/", $subject);
    }

    private function isNil($subject) {
        return preg_match("/^nil\@nil/", $subject);
    }

    private function parseVar($subject) {
        $operandParts = explode("@", $subject);
        return strtoupper($operandParts[0]) . "@" . $operandParts[1];
    }

    private function parseVal($subject) {
        return explode("@", $subject)[1];
    }

    private function actualEqualsExpected($actualLineParts, $expectedOperands) {
        if (count($actualLineParts) - 1 != count($expectedOperands)) {
            error_log("Wrong number of operands for instruction: " . $actualLineParts[0]);
            return false;
        }

        for ($i = 0; $i < count($expectedOperands); $i++) {
            $isValid = ArgType::isArgValid($expectedOperands[$i], $actualLineParts[$i + 1]);
            if ($isValid == false) {
                return false;
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
        $program = new Program("IPPcode20");

        $instr = $this->instParser->getNextInstruction();

        while ($instr instanceof Instruction) {
            $program->appendInstruction($instr);
            $instr = $this->instParser->getNextInstruction();
        }

        // is error code?
        if (is_numeric($instr)) { 
            return $instr;
        }

        return $program;
    }
}

class Program
{
    private $instructions = array(), $language;

    public function __construct($language) {
        $this->language = $language;
    }

    public function appendInstruction($instruction) {
        array_push($this->instructions, $instruction);
    }

    public function getLanguage() {
        return $this->language;
    }

    public function getInstructions() {
        return $this->instructions;
    }
}

class Instruction
{
    private $opcode, $args;

    public function __construct($opcode, $args) {
        $this->opcode = $opcode;
        $this->args = $args;
    }

    public function getOpcode() {
        return $this->opcode;
    }

    public function getArgs() {
        return $this->args;
    }
}

class Arg
{
    private $type, $content;

    public function __construct($type, $content) {
        $this->type = $type;
        $this->content = $content;
    }

    public function getType() {
        return $this->type;
    }

    public function getContent() {
        return $this->content;
    }
}

class ArgType
{
    const INT = "int";
    const BOOL = "bool";
    const STRING = "string";
    const NIL = "nil";
    const LABEL = "label";
    const TYPE = "type";
    const VAR = "var";
    const SYMB = "symb";

    public static function isArgValid($expectedArgType, $arg) {
        
        return true; // todo
    }
}

class XmlProgramSerializer implements IProgramSerializer
{
    public function serialize($program) {
        $dom = $this->createNew();
        // create Program element
        $root = $dom->createElement("program");
        $language = new DOMAttr("language", $program->getLanguage());
        $root->setAttributeNode($language);
 
        // create Instruction elements
        $instructions = $program->getInstructions();
        for ($i = 1; $i <= count($instructions); $i++) {
            $instr = $instructions[$i - 1];
            $instrElement = $this->createInstruction($dom, $instr, $i);
            $root->appendChild($instrElement);
        }
        $dom->appendChild($root);

        $xml_string = $dom->saveXML();
        echo $xml_string;
    }

    private function createNew() {
        $dom = new DOMDocument();
		$dom->encoding = 'UTF-8';
		$dom->xmlVersion = '1.0';
        $dom->formatOutput = true;
        return $dom;
    }

    private function createInstruction($dom, $instr, $index) {
        $instrElement = $dom->createElement('instruction');
        $order = new DOMAttr("order", $index);
        $opcode = new DOMAttr("opcode", $instr->getOpcode());
        $instrElement->setAttributeNode($order);
        $instrElement->setAttributeNode($opcode);

        $args = $instr->getArgs();
        if (is_null($args)) {
            return $instrElement;
        }
        for ($i = 1; $i <= count($args); $i++) {
            $arg = $args[$i - 1];
            $argElement = $dom->createElement("arg" . $i);
            $type = new DOMAttr("type", $arg->getType());
            $argElement->setAttributeNode($type);
            $content = $this->encodeString($arg->getContent());
            $argElement->textContent = $content;
            $instrElement->appendChild($argElement);
        }

        return $instrElement;
    }

    private function encodeString($string) {
        return htmlspecialchars($string, ENT_XML1, 'UTF-8');
    }
    private function addArgument($root, $instr) {

    }
}

$main = new Main();
$returnCode = $main->begin();
exit($returnCode);
?>