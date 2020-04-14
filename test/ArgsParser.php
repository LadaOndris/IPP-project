<?php

/**
 * ArgsParser parses the arguments for parse.php.
 */
class ArgsParser
{
    private $argv;

    public function __construct($argv) {
        $this->argv = $argv;
    }

    /**
     * Parses arguments of the parse.php script and returns an Args object containing
     * the arguments or their default values.
     */
    public function parse() {
        $args = new Args();
        $isIntOnlySet = $isParseOnlySet = false;
        $isIntScriptSet = $isParseScriptSet = false;
        $isTestlistSet = false;
        $isDirectorySet = false;


        for ($i = 1; $i < count($this->argv); $i++) {
            switch ($this->argv[$i]) {
                case "--verbose":  $args->verbose = true; break;
                case "--help":  $args->help = true; break;
                case "--recursive": $args->recursive = true; break;
                case "--parse-only": $args->parseOnly = true; $isParseOnlySet = true; break;
                case "--int-only": $args->intOnly = true; $isIntOnlySet = true; break;
                default: {
                    $arg = $this->argv[$i];
                    if ($this->isValueArgument("directory", $arg)) {
                        $args->directory = $this->parseValueArgument($arg);
                        $this->checkDirectoryExists($args->directory, "--directory");
                        $isDirectorySet = true;
                    }
                    else if ($this->isValueArgument("parse-script", $arg)) {
                        $args->parseScript = $this->parseValueArgument($arg);
                        $this->checkFileExists($args->parseScript, "--parse-only");
                        $isParseScriptSet = true;
                    }
                    else if ($this->isValueArgument("int-script", $arg)) {
                        $args->intScript = $this->parseValueArgument($arg);
                        $this->checkFileExists($args->intScript, "--int-only");
                        $isIntScriptSet = true;
                    }
                    else if ($this->isValueArgument("jexamxml", $arg)) {
                        $args->jexamxml = $this->parseValueArgument($arg);
                        $this->checkFileExists($args->jexamxml, "--jexamxml");
                    }
                    else if ($this->isValueArgument("match", $arg)) {
                        $args->match = $this->parseValueArgument($arg);
                    }
                    else if ($this->isValueArgument("testlist", $arg)) {
                        $args->testlist = $this->parseValueArgument($arg);
                        $this->checkFileExists($args->testlist, "--testlist");
                        $isTestlistSet = true;
                    }
                    else {
                        throw new Exception("Invalid argument: " . $arg, Errors::INVALID_ARGUMENT);
                    }
                }
            }
        }
        if ($isDirectorySet && $isTestlistSet) {
            throw new Exception("Parameter --directory cannot be combined with --testlist.", Errors::INVALID_COMBINATION_OF_PARAMS);
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
        if (!$args->help) {
            if ($args->parseOnly) {
                $this->checkFileExists($args->parseScript, "--parse-only");
                $this->checkFileExists($args->jexamxml, "--jexamxml");
            }
            else if ($args->intOnly) {
                $this->checkFileExists($args->intScript, "--int-only");
            }
            else {
                $this->checkFileExists($args->parseScript, "--parse-only");
                $this->checkFileExists($args->intScript, "--int-only");
                $this->checkFileExists($args->jexamxml, "--jexamxml");
            }
        }
        return $args;
    }

    private function checkFileExists($file, $optionName) {
        if (!$this->fileExists($file))
            throw new Exception("Option {$optionName} is invalid. '{$file}' is not a file.", Errors::OPEN_INPUT_FILE_ERROR);
    }

    private function checkDirectoryExists($dir, $optionName) {
        if (!$this->directoryExists($dir))
            throw new Exception("Option {$optionName} is invalid. '{$dir}' is not a directory.", Errors::INVALID_ARGUMENT);
    }

    private function fileExists($file) {
        return file_exists($file) and !is_dir($file);
    }

    private function directoryExists($directory) {
        return file_exists($directory) and is_dir($directory);
    }

    private function isValueArgument($argumentName, $argument) {
        return preg_match("/--".$argumentName."=.+/", $argument);
    }

    private function parseValueArgument($argument) {
        return explode("=", $argument)[1];
    }
}

/**
 * Arguments of the parse.php script.
 */
class Args
{
    public $help = false;
    public $verbose = false;
    public $directory = ".";
    public $recursive = false;
    public $parseScript = "./parse.php";
    public $intScript = "./interpret.py";
    public $parseOnly = false;
    public $intOnly = false;
    public $jexamxml = "/pub/courses/ipp/jexamxml/jexamxml.jar";
    public $match = ".*";
    public $testlist;
}

?>