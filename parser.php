<?php

interface IProgramParser
{
    // returns an instance of Program class
    public function parse();
}

interface IInstructionParser
{
    // returns an instance of Instruction class
    public function getNextInstruction();
}

interface IArgParser
{
    // returns an instance of Arg class
    public function parseArg($expectedArgumentType, $actualArgument);
}

interface IInputReader
{
    public function readNextLine();
    public function getCommentsCount();
}

interface IProgramSerializer
{
    public function serialize($program);
}

class Errors
{
    const INVALID_COMBINATION_OF_ARGUMENTS = 10;
    const INVALID_ARGUMENT = 10;
    const MISSING_ARGUMENT = 10;

    const INVALID_HEADER = 21;
    const INVALID_INSTRUCTION_OPCODE = 22;
    const INVALID_ARGUMENT_TYPE = 23;
    const INVALID_OPERANDS_COUNT = 23;
}

class StdinInputReader implements IInputReader 
{
    private $commentsCount = 0;

    public function readNextLine() {
        return $this->readNextNonEmptyLine();
    }

    private function readLine() {
        return fgets(STDIN);;
    }
    
    private function readNextNonEmptyLine() {
        do {
            $line = $this->readLine();
            if (!$line) {   
                return NULL;
            }

            $line = trim($line); // get rid of white spaces
            $parts = explode("#", $line); // get rid of comments
            if (count($parts) > 1) {
                $this->commentsCount++;
            }
            $line = $parts[0];
            $parts = preg_split("/\s+/", $line, 0, PREG_SPLIT_NO_EMPTY);
        } while(count($parts) == 0);
        return $parts;
    }

    public function getCommentsCount() {
        return $this->commentsCount;
    }
}

class InstructionParser implements IInstructionParser
{
    private $reader;
    private $argParser;
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
        "NOT" => array(ArgType::VAR, ArgType::SYMB),
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

    public function __construct(IInputReader $reader, IArgParser $argParser) {
        $this->reader = $reader;
        $this->argParser = $argParser;
    }

    /**
     * Returns a next instruction parsed from the input.
     * Returns NULL if there is no more input.
     */
    public function getNextInstruction() {
        // read line and reformat
        $parts = $this->reader->readNextLine();
        if ($parts === NULL) {
            return NULL;
        }
        $parts[0] = strtoupper($parts[0]);
        
        if (array_key_exists($parts[0], $this->expectedOperandsList) == false) {
            throw new Exception("Invalid instruction opcode: " . $parts[0], Errors::INVALID_INSTRUCTION_OPCODE);
        }
        $expectedOperands = $this->expectedOperandsList[$parts[0]];
        return $this->createInstruction($parts, $expectedOperands);
    }

    private function createInstruction($parts, $expectedOperands) {
        $opcode = $parts[0];
        $args = $this->createArgs($parts, $expectedOperands);
        return new Instruction($opcode, $args);
    }

    private function createArgs($parts, $operandTypes) {
        if (count($parts) - 1 != count($operandTypes)) {
            throw new Exception("Wrong number of operands for instruction: " . $parts[0], Errors::INVALID_OPERANDS_COUNT);
        }
        $args = array();
        for ($i = 0; $i < count($operandTypes); $i++) {
            $operandType = $operandTypes[$i];
            $operand = $parts[$i + 1];

            $arg = $this->argParser->parseArg($operandType, $operand);
            array_push($args, $arg);
        }
        return $args;
    }
}

class ArgParser implements IArgParser
{
    public function parseArg($expectedArgumentType, $actualArgument) {
        $argumentType = $expectedArgumentType;
        switch ($expectedArgumentType) {
            case ArgType::TYPE:
                if ($this->isType($actualArgument))
                    return $this->newTypeArg($actualArgument);
                break;
            case ArgType::VAR:
                if ($this->isVar($actualArgument))
                    return $this->newVarArg($actualArgument);
                break;
            case ArgType::LABEL:
                return new Argument(ArgType::LABEL, $actualArgument);
                break;
            case ArgType::NIL:
                if ($this->isNil($actualArgument))
                    return $this->newNilArg($actualArgument);
                break;
            case ArgType::SYMB: {
                if ($this->isVar($actualArgument)) {
                    return $this->newVarArg($actualArgument);
                }
                elseif ($this->isString($actualArgument)) {
                    return $this->newStringArg($actualArgument);
                }
                elseif ($this->isInt($actualArgument)) {
                    return $this->newIntArg($actualArgument);
                }
                elseif ($this->isBool($actualArgument)) {
                    return $this->newBoolArg($actualArgument);
                }
                elseif ($this->isNil($actualArgument)) {
                    return $this->newNilArg($actualArgument);
                }
                else {
                    throw new Exception("Expected SYMB argument, but the format is invalid", Errors::INVALID_ARGUMENT_TYPE);
                }
            } break;
            default: {
                throw new Exception("Undefined ArgType value.", Errors::INVALID_ARGUMENT_TYPE);
            }
        }
        throw new Exception("Invalid ArgType value.", Errors::INVALID_ARGUMENT_TYPE);
    }

    private function newTypeArg($actualArgument) {
        return new Argument(ArgType::TYPE, $actualArgument);
    }

    private function newIntArg($actualArgument) {
        $content = $this->parseVal($actualArgument);
        return new Argument(ArgType::INT, $content);
    }

    private function newBoolArg($actualArgument) {
        $content = $this->parseVal($actualArgument);
        return new Argument(ArgType::BOOL, $content);
    }

    private function newStringArg($actualArgument) {
        $content = $this->parseVal($actualArgument);
        return new Argument(ArgType::STRING, $content);
    }

    private function newNilArg($actualArgument) {
        $content = $this->parseVal($actualArgument);
        return new Argument(ArgType::NIL, $content); // todo, nil?
    }
    
    private function newVarArg($actualArgument) {
        $content = $this->parseVar($actualArgument);
        return new Argument(ArgType::VAR, $content);
    }

    private function isType($subject) {
        return preg_match("/^(int|bool|string)$/", $subject);
    }

    private function isVar($subject) {
        $variableRegex = "/^GF@[[:alpha:]" . $this->specialChars . "][[:alnum:]" . $this->specialChars . "]*$/";
        return preg_match($variableRegex, $subject);
    }

    private function isString($subject) {
        return preg_match("/^string@(([^\\\#]|\\\\\d{3})+|$)/", $subject);
    }
    
    private function isInt($subject) {
        return preg_match("/^int\@.+$/", $subject);
    }
    
    private function isBool($subject) {
        return preg_match("/^bool\@(true|false)$/", $subject);
    }

    private function isNil($subject) {
        return preg_match("/^nil\@nil$/", $subject);
    }

    private function parseVar($subject) {
        preg_match("/(.+)@(.+)/", $subject, $matches);
        return strtoupper($matches[1]) . "@" . $matches[2];
    }

    private function parseVal($subject) {
        preg_match("/.+@(.*)/", $subject, $matches);
        return $matches[1];
    }

    private $specialChars = "_\-\$&%\*!\?";
}
 

class ProgramParser implements IProgramParser
{
    private $instParser;
    private $lineReader;
    private $program;

    public function __construct(IInstructionParser $instParser, IInputReader $lineReader) {
        $this->instParser = $instParser;
        $this->lineReader = $lineReader;
    }

    public function parse() {
        $this->checkProgramHeader();
        $this->program = new Program("IPPcode20");
        $this->loadInstructions();
        $this->program->setCommentsCount($this->lineReader->getCommentsCount());
        return $this->program;
    }

    private function checkProgramHeader() {
        $inputParts = $this->lineReader->readNextLine();
        if (count($inputParts) != 1 || $this->isHeaderValid($inputParts[0]) == false) {
            throw new Exception("Invalid header", Errors::INVALID_HEADER);
        }
    }

    private function isHeaderValid($header) {
        return trim($header) == '.IPPcode20';
    }

    private function loadInstructions() {
        $instr = $this->instParser->getNextInstruction();
        while ($instr instanceof Instruction) {
            $this->program->appendInstruction($instr);
            $instr = $this->instParser->getNextInstruction();
        }

    }
}

class Program
{
    private $instructions = array(), $language, $commentsCount;

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

    public function setCommentsCount($commentsCount) {
        $this->commentsCount = $commentsCount;
    }

    public function getCommentsCount() {
        return $this->commentsCount;
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

class Argument
{
    protected $argumentType, $content;

    public function __construct($type, $content) {
        $this->argumentType = $type;
        $this->content = $content;
    }

    public function getType() {
        return $this->argumentType;
    }

    public function getContent() {
        return $this->content;
    }

}

abstract class ArgType {
    const INT = "int";
    const BOOL = "bool";
    const STRING = "string";
    const NIL = "nil";
    const LABEL = "label";
    const TYPE = "type";
    const VAR = "var";
    const SYMB = "symb";
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
        return htmlspecialchars($string, ENT_XML1 | ENT_QUOTES, 'UTF-8');
    }
}

class Statistics
{
    const LOC = "loc";
    const COMMENTS = "comments";
    const LABELS = "labels";
    const JUMPS = "jumps";

    private $jumpInstructions = array("CALL", "RETURN", "JUMP", "JUMPIFEQ", "JUMPIFNEQ");
    private $instructionsCount, $commentsCount, $labelsCount, $jumpInstructionsCount;

    public function __construct($file, $requestedStats) {
        $this->file = $file;
        $this->requestedStats = $requestedStats;
    }

    public function createStatistics($program) {
        if (!$this->file) {
            return;
        }
        $this->setStatistics($program);
        $this->writeStatistics();
    }

    private function setStatistics($program) {
        $instructions = $program->getInstructions();
        $this->instructionsCount = count($instructions);
        $this->commentsCount = $program->getCommentsCount();
        $this->labelsCount = $this->countLabels($instructions);
        $this->jumpInstructionsCount = $this->countJumpInstructions($instructions);
    }

    private function countLabels($instructions) {
        $labels = array();
        foreach ($instructions as $instruction) {
            $args = $instruction->getArgs();
            foreach ($args as $arg) {
                if ($arg->getType() == ArgType::LABEL && 
                    !in_array($arg->getContent(), $labels)) {
                    array_push($labels, $arg->getContent());
                }
            }
        }
        return count($labels);
    }

    private function countJumpInstructions($instructions) {
        $jumps = 0;
        foreach ($instructions as $instruction) {
            if ($this->isJumpInstruction($instruction)) {
                $jumps++;
            }
        }
        return $jumps;
    }

    private function isJumpInstruction($instruction) {
        $opcode = $instruction->getOpcode();
        return in_array($opcode, $this->jumpInstructions);
    }

    private function writeStatistics() {
        $file = fopen($this->file, "w"); 
        foreach ($this->requestedStats as $stat) {
            $this->writeStatisticToFile($stat, $file);
        }
        fclose($file);
    }

    private function writeStatisticToFile($stat, $file) {
        // switch statement? should be polymorphic? should we rather use an array?
        switch ($stat) {
            case Statistics::LOC: fwrite($file, $this->instructionsCount); break;
            case Statistics::COMMENTS: fwrite($file, $this->commentsCount); break;
            case Statistics::LABELS: fwrite($file, $this->labelsCount); break;
            case Statistics::JUMPS: fwrite($file, $this->jumpInstructionsCount); break;
        }
        fwrite($file, "\n");
    }
}

class ArgsParser
{
    private $argv;

    public function __construct($argv) {
        $this->argv = $argv;
    }

    public function parse() {
        $args = $this->loadArguments();
        $this->checkArgumentsValidity($args);
        return $args;
    }

    private function loadArguments() {
        $args = new Args();
        for ($i = 1; $i < count($this->argv); $i++) {
            switch ($this->argv[$i]) {
                case "--help":  $args->help = true; break;
                case "--loc": array_push($args->statsOptions, Statistics::LOC); break;
                case "--comments": array_push($args->statsOptions, Statistics::COMMENTS); break;
                case "--labels": array_push($args->statsOptions, Statistics::LABELS); break;
                case "--jumps": array_push($args->statsOptions, Statistics::JUMPS); break;
                default: {
                    if (preg_match("/^--stats=.+/", $this->argv[$i])) {
                        $args->statsFile = explode("=", $this->argv[$i])[1];
                    }
                    else {
                        throw new Exception("Invalid argument: " . $this->argv[$i], Errors::INVALID_ARGUMENT);
                    }
                } 
            }
        }
        return $args;
    }

    private function checkArgumentsValidity($args) {
        if (count($args->statsOptions) > 0 && !$args->statsFile) {
            throw new Exception("--statsFile parameter wasn't defined", Errors::MISSING_ARGUMENT);
        }
        if ($args->help && (count($args->statsOptions) > 0 || $args->statsFile)) {
            throw new Exception("--help cannot be combined with any other parameter", Errors::INVALID_COMBINATION_OF_ARGUMENTS);
        }
    }
}

class Args {
    public $help = false;
    public $statsOptions = array();
    public $statsFile = NULL;
}

try {
    $argsParser = new ArgsParser($argv);
    $args = $argsParser->parse();

    $statistics = new Statistics($args->statsFile, $args->statsOptions);
    $inputReader = new StdinInputReader();
    $argParser = new ArgParser();
    $instParser = new InstructionParser($inputReader, $argParser);
    $programParser = new ProgramParser($instParser, $inputReader);
    $serializer = new XmlProgramSerializer();

    $parseResult = $programParser->parse();
    $serializer->serialize($parseResult);
    $statistics->createStatistics($parseResult);
}
catch (Exception $e) {
    error_log($e->getMessage());
    exit($e->getCode());
}

?>