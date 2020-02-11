<?php

try {
    $argsParser = new ArgsParser($argv);
    $args = $argsParser->parse();
    $testSuiteReader = new DirectoryTestSuiteReader($args->recursive);
    $testSuiteReader = new PreprocessTestSuiteReader($testSuiteReader);
    $testSuites = $testSuiteReader->read();
}
catch (Exception $e) {
    error_log($e->getMessage());
    exit($e->getCode());
}

class Errors
{
    const INVALID_COMBINATION_OF_PARAMS = 10;
    const INVALID_ARGUMENT = 10;
}

class ArgsParser
{
    private $argv;

    public function __construct($argv) {
        $this->argv = $argv;
    }

    public function parse() {
        $args = new Args();
        $isIntOnlySet = $isParseOnlySet = false;
        $isIntScriptSet = $isParseScriptSet = false;

        for ($i = 1; $i < count($this->argv); $i++) {
            switch ($this->argv[$i]) {
                case "--help":  $args->help = true; break;
                case "--recursive": $args->recursive = true; break;
                case "--parse-only": $args->parseOnly = true; $isParseOnlySet = true; break;
                case "--int-only": $args->intOnly = true; $isIntOnlySet = true; break;
                default: {
                    $arg = $this->argv[$i];
                    if ($this->isFileArgument("directory", $arg)) {
                        $args->directory = $this->parseFileArgument($arg);
                    }
                    if ($this->isFileArgument("parse-script", $arg)) {
                        $args->parseScript = $this->parseFileArgument($arg);
                        $isParseScriptSet = true;
                    }
                    if ($this->isFileArgument("int-script", $arg)) {
                        $args->intScript = $this->parseFileArgument($arg);
                        $isIntScriptSet = true;
                    }
                    if ($this->isFileArgument("jexamxml-script", $arg)) {
                        $args->jexamxml = $this->parseFileArgument($arg);
                    }
                    else {
                        throw new Exception("Invalid argument", Errors::INVALID_ARGUMENT);
                    }
                } 
            }
        }
        if ($isIntOnlySet && ($isParseOnlySet || $isParseScriptSet)) {
            throw new Exception("Parameter --int-only cannot be combined with --parse-only.", Errors::INVALID_COMBINATION_OF_PARAMS);
        }
        if ($isParseOnlySet && ($isIntOnlySet || $isIntScriptSet)) {
            throw new Exception("Parameter --parse-only cannot be combined with --int-only.", Errors::INVALID_COMBINATION_OF_PARAMS);
        }
        if ($args->help && count($this->argv) > 2) {
            throw new Exception("Parameter --help cannot be combined with any other.", Errors::INVALID_COMBINATION_OF_PARAMS);
        }
        return $args;
    }

    private function isFileArgument($argumentName, $argument) {
        return preg_match("/--".$argumentName."=.+/", $argument);
    }

    private function parseFileArgument($argument) {
        return explode("=", $argument)[1];
    }
    
    public function getErrors() {
        return $this->errors;
    }
}

class Args
{
    public $help = false;
    public $directory = "./";
    public $recursive = false;
    public $parseScript = "./parse.php";
    public $intScript = "./interpret.py";
    public $parseOnly = false;
    public $intOnly = false;
    public $jexamxml = "/pub/courses/ipp/jexamxml/jexamxml.jar";
}

class TestCaseResult
{
    private $testCase;
    private $hasPassed;

    public function __construct($testCase, $hasPassed) {
        $this->testCase = $testCase;
        $this->hasPassed = $hasPassed;
    }
}

class TestSuiteResult
{
    private $testCaseResults;

    public function __construct($testCaseResults) {
        $this->testCaseResults = $testCaseResults;
    }

    public function getTotalPassed() {

    }

    public function getTotalFailed() {

    }
}

class TestCaseType
{
    const INT_ONLY = 1;
    const PARSE_ONLY = 2;
    const INT_AND_PARSE = 3;
}

class TestCase
{
    private $name;
    private $type; // int-only, parse-only, int-and-parse

    public function __construct($name, $type) {
        $this->name = $name;
        $this->type = $type;
    }

    public function run() {

    }
}

class TestSuite
{
    private $directory;
    
    public function __construct($directory) {
        $this->directory = $directory;
    }

    public function run() {
        
    }
}

interface ITestSuiteReader
{
    public function read(); // returns a set of testsuites
}

interface ISummaryGenerator
{
    public function generate($testSuiteResults);
}

class DirectoryTestSuiteReader implements ITestSuiteReader
{
    private $recursively;

    public function __construct($recursively) {
        $this->recursively = $recursively;
    }

    public function read() {
        $testSuites = array();

        return $testSuites;
    }
}

class PreprocessTestSuiteReader implements ITestSuiteReader
{
    private $testSuiteReader;

    public function __construct($reader) {
        $this->testSuiteReader = $reader;
    }

    public function read() {
        $testSuites = $this->testSuiteReader->read();
        // create empty in and out files if they don't exist

        // create rc file with "0" if it doesn't exist

    }
}

class HtmlGenerator implements ISummaryGenerator
{
    public function generate($testSuiteResults) {
        
    }
}


?>