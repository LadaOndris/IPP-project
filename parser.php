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
}

interface IProgramSerializer
{
    public function serialize($program);
}

class Parser
{
    public function __construct($statistics) {
        $this->statistics = $statistics;
        $this->reader = new StdinInputReader();
        $argParser = new ArgParser();
        $instParser = new InstructionParser($this->reader, $argParser);
        $this->programParser = new ProgramParser($instParser);
        $this->serializer = new XmlProgramSerializer();
    }

    public function begin() {
        $parseResult = $this->programParser->parse();
        if (is_numeric($parseResult)) {
            return $parseResult;
        }
        $this->serializer->serialize($parseResult);
        $this->statistics->createStatistics($parseResult);
        return 0;
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
    private $commentsCount = 0;
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

    public function __construct($reader, $argParser) {
        $this->reader = $reader;
        $this->argParser = $argParser;
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
            $parts = explode("#", $line); // get rid of comments
            if (count($parts) > 1) {
                $this->commentsCount++;
            }
            $line = $parts[0];
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
        $args = $this->createArgs($parts, $expectedOperands);
        if (is_numeric($args)) // is error
            return $args;
        return new Instruction($opcode, $args);
    }

    private function createArgs($parts, $operandTypes) {
        if (count($parts) - 1 != count($operandTypes)) {
            error_log("Wrong number of operands for instruction: " . $operandTypes[0]);
            return 23;
        }
        $args = array();
        for ($i = 0; $i < count($operandTypes); $i++) {
            $operandType = $operandTypes[$i];
            $operand = $parts[$i + 1];

            $arg = $this->argParser->parseArg($operandType, $operand);
            if (is_numeric($arg)) // is error
                return $arg;
            array_push($args, $arg);
        }
        return $args;
    }

    public function getCommentsCount() {
        return $this->commentsCount;
    }
}

class ArgParser implements IArgParser
{
    public function parseArg($expectedArgumentType, $actualArgument) {
        $error = 23;
        $argumentType = $expectedArgumentType;
        switch ($expectedArgumentType) {
            case ArgType::TYPE:
                if ($this->isType($actualArgument))
                    return $this->newTypeArg($actualArgument);
            case ArgType::VAR:
                if ($this->isVar($actualArgument))
                    return $this->newVarArg($actualArgument);
            case ArgType::LABEL:
                return new Arg(ArgType::LABEL, $actualArgument);
            case ArgType::NIL:
                if ($this->isNil($actualArgument))
                    return $this->newNilArg($actualArgument);
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
                    return $error;
                }
            } break;
            default: {
                error_log("Undefined ArgType value.");
                return $error;
            }
        }
        return $error;
    }

    private function newTypeArg($actualArgument) {
        return new Arg(ArgType::TYPE, $actualArgument);
    }

    private function newIntArg($actualArgument) {
        $content = $this->parseVal($actualArgument);
        return new Arg(ArgType::INT, $content);
    }

    private function newBoolArg($actualArgument) {
        $content = $this->parseVal($actualArgument);
        return new Arg(ArgType::BOOL, $content);
    }

    private function newStringArg($actualArgument) {
        $content = $this->parseVal($actualArgument);
        return new Arg(ArgType::STRING, $content);
    }

    private function newNilArg($actualArgument) {
        $content = $this->parseVal($actualArgument);
        return new Arg(ArgType::NIL, $content); // todo, nil?
    }
    
    private function newVarArg($actualArgument) {
        $content = $this->parseVar($actualArgument);
        return new Arg(ArgType::VAR, $content);
    }

    private function isType($subject) {
        return preg_match("/^(int|bool|string)/", $subject);
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

}

class ProgramParser implements IProgramParser
{
    private $instParser, $lineReader;

    public function __construct($instParser, $lineReader) {
        $this->instParser = $instParser;
        $this->lineReader = $lineReader;
    }

    public function parse() {
        $inputHeader = $this->lineReader->readNextLine();
        if ($this->isHeaderValid($inputHeader) == false) {
            return 21;
        }

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

        $program->setCommentsCount($this->instParser->getCommentsCount());
        return $program;
    }

    private function isHeaderValid($header) {
        return trim($header) == '.IPPcode20';
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
}

class Statistics
{
    const LOC = "loc";
    const COMMENTS = "comments";
    const LABELS = "labels";
    const JUMPS = "jumps";

    public function __construct($file, $requestedStats) {
        $this->file = $file;
        $this->requestedStats = $requestedStats;
    }

    public function createStatistics($program) {
        if (!$this->file) {
            return;
        }
        $file = fopen($this->file, "w"); 

        $instructions = $program->getInstructions();
        $loc = count($instructions);
        $comments = $program->getCommentsCount();
        $labels = $this->countLabels($instructions);
        $jumps = $this->countJumps($instructions);

        foreach ($this->requestedStats as $stat) {
            switch ($stat) {
                case Statistics::LOC: fwrite($file, $loc); break;
                case Statistics::COMMENTS: fwrite($file, $comments); break;
                case Statistics::LABELS: fwrite($file, $labels); break;
                case Statistics::JUMPS: fwrite($file, $jumps); break;
            }
            fwrite($file, "\n");
        }
        fclose($file);
    }

    private function countLabels($instructions) {
        $labels = 0;
        foreach ($instructions as $instruction) {
            $args = $instruction->getArgs();
            foreach ($args as $arg) {
                if ($arg->getType() == ArgType::LABEL)
                    $labels++;
            }
        }
        return $labels;
    }

    private function countJumps($instructions) {
        $jumps = 0;
        foreach ($instructions as $instruction) {
            $opcode = $instruction->getOpcode();
            if ($opcode == "CALL" ||
                $opcode == "RETURN" ||
                $opcode == "RETURN" ||
                $opcode == "JUMP" ||
                $opcode == "JUMPIFEQ" ||
                $opcode == "JUMPIFNEQ") {
                $jumps++;
            }
        }
        return $jumps;
    }
}

$statsOptions = array();
$statsFile = NULL;

for ($i = 1; $i < count($argv); $i++) {
    switch ($argv[$i]) {
        case "--help":  $help = true; break;
        case "--loc": array_push($statsOptions, Statistics::LOC); break;
        case "--comments": array_push($statsOptions, Statistics::COMMENTS); break;
        case "--labels": array_push($statsOptions, Statistics::LABELS); break;
        case "--jumps": array_push($statsOptions, Statistics::JUMPS); break;
        default: {
            if (preg_match("/^--stats=.+/", $argv[$i])) {
                $statsFile = explode("=", $argv[$i])[1];
            }
            else {
                exit(10);
            }
        } 
    }
}

if (count($statsOptions) > 0 && !$statsFile) {
    exit(10); // statsFile parameter wasn't defined
}
// help cannot be combined with any other parameter
if ($help && (count($statsOptions) > 0 || $statsFile)) {
    exit(10);
}

$stats = new Statistics($statsFile, $statsOptions);
$parser = new Parser($stats);
$returnCode = $parser->begin();
exit($returnCode);

?>