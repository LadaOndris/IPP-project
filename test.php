<?php

$argsParser = new ArgsParser($argv);
$args = $argsParser->parse();


new Test();
new TestSuite(); // consists of tests

new TestRunner(); // 


class ArgsParser
{
    private $errors = array();
    private $argv;

    public function __construct($argv) {
        $this->argv = $argv;
    }

    public function parse() {
        $args = new Args();

        for ($i = 1; $i < count($argv); $i++) {
            switch ($argv[$i]) {
                case "--help":  $args->help = true; break;
                case "--recursive": $args->recursive = true; break;
                case "--parse-only": $args->parseOnly = true; break;
                case "--int-only": $args->intOnly = true; break;
                default: {
                    $arg = $argv[$i];
                    if ($this->isFileArgument("directory", $arg)) {
                        $args->directory = $this->parseFileArgument($arg);
                    }
                    if ($this->isFileArgument("parse-script", $arg)) {
                        $args->parseScript = $this->parseFileArgument($arg);
                    }
                    if ($this->isFileArgument("int-script", $arg)) {
                        $args->intScript = $this->parseFileArgument($arg);
                    }
                    if ($this->isFileArgument("jexamxml-script", $arg)) {
                        $args->jexamxml = $this->parseFileArgument($arg);
                    }
                    else {
                        array_push($this->errors, 10);
                    }
                } 
            }
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

class TestResult
{

}




?>