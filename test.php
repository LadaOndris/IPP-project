<?php

class Errors
{
    const INVALID_COMBINATION_OF_PARAMS = 10;
    const INVALID_ARGUMENT = 10;
    const OPEN_INPUT_FILE_ERROR = 11;
    const OPEN_OUTPUT_FILE_ERROR = 12;
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
                    else if ($this->isFileArgument("parse-script", $arg)) {
                        $args->parseScript = $this->parseFileArgument($arg);
                        $isParseScriptSet = true;
                    }
                    else if ($this->isFileArgument("int-script", $arg)) {
                        $args->intScript = $this->parseFileArgument($arg);
                        $isIntScriptSet = true;
                    }
                    else if ($this->isFileArgument("jexamxml-script", $arg)) {
                        $args->jexamxml = $this->parseFileArgument($arg);
                    }
                    else {
                        throw new Exception("Invalid argument: " . $arg, Errors::INVALID_ARGUMENT);
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
}

class Args
{
    public $help = false;
    public $directory = ".";
    public $recursive = false;
    public $parseScript = "./parser.php";
    public $intScript = "./interpret.py";
    public $parseOnly = false;
    public $intOnly = false;
    public $jexamxml = "/pub/courses/ipp/jexamxml/jexamxml.jar";
}

class TestCaseResult
{
    private $testCase;
    private $hasPassed;

    public function __construct(TestCase $testCase, $hasPassed) {
        $this->testCase = $testCase;
        $this->hasPassed = $hasPassed;
    }

    public function hasPassed() {
        return $this->hasPassed;
    }

    public function getTestCase() {
        return $this->testCase;
    }
}

class TestSuiteResult
{
    private $testCaseResults;
    private $testSuite;

    public function __construct(TestSuite $testSuite, $testCaseResults) {
        $this->testSuite = $testSuite;
        $this->testCaseResults = $testCaseResults;
    }

    public function getTotalPassed() {
        $totalPassed = 0;
        foreach ($this->testCaseResults as $testCaseResult) {
            if ($testCaseResult->hasPassed()) {
                $totalPassed++;
            }
        }
        return $totalPassed;
    }

    public function getTotalFailed() {
        return count($this->testCaseResults) - $this->getTotalPassed();
    }

    public function getTestSuite() {
        return $this->testSuite;
    }
}

class TestCase
{
    private $path;
    private $name;

    public function __construct($path, $name) {
        $this->path = $path;
        $this->name = $name;
    }

    public function getPath() {
        return $this->path;
    }

    public function getName() {
        return $this->name;
    }

    public function getPathname() {
        return $this->path . DIRECTORY_SEPARATOR . $this->name;
    }

    private function getSourceFilename() {
        return $this->getPathname() . ".src";
    }

    private function getInputFilename() {
        return $this->getPathname() . ".in";
    }
    
    private function getOutputFilename() {
        return $this->getPathname() . ".out";
    }

    private function getReturnCodeFilename() {
        return $this->getPathname() . ".rc";
    }
}

class TestSuite
{
    private $directory;
    private $testCases;
    
    public function __construct($directory, $testCases) {
        $this->directory = $directory;
        $this->testCases = $testCases;
    }
    public function getDirectory() {
        return $this->directory;
    }

    public function getTestCases() {
        return $this->testCases;
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

interface ITestRunner
{
    public function runTest(TestCase $test);
}

class FilenameFilter extends FilterIterator 
{
    private $regex;

    public function __construct(Iterator $it, $regex) {
        $this->regex = $regex;
        parent::__construct($it);
    }

    public function accept() {
        return $this->isFile() && preg_match($this->regex, $this->getFilename());
    }
}

class DirectoryTestSuiteReader implements ITestSuiteReader
{
    private $directory;
    private $recursively;

    public function __construct($directory, $recursively) {
        $this->directory = $directory;
        $this->recursively = $recursively;
    }

    public function read() {
        $testSuites = array();

        $dirs = $this->getSubDirectories($this->directory, $this->recursively);
        array_push($dirs, $this->directory);
        
        foreach ($dirs as $dir) {
            $testCases = $this->getTestCases($dir);
            $testSuite = new TestSuite($dir, $testCases);
            array_push($testSuites, $testSuite);
        }
        return $testSuites;
    }

    private function getSubDirectories($directory, $recursively) {
        $dirs = array();
        $files = scandir($directory);
        foreach ($files as $file) {
            $dirPath = $directory . DIRECTORY_SEPARATOR . $file;
            if (is_dir($dirPath)) {
                if (basename($dirPath) == "." || basename($dirPath) == "..")
                    continue;
                array_push($dirs, $dirPath);

                if ($recursively) {
                    $dirsRecursive = $this->getSubDirectories($dirPath, $recursively);
                    $dirs = array_merge($dirsRecursive, $dirs);
                }
            }
        }
        return $dirs;
    }

    private function getTestCases($directory) {
        $testCases = array();
        $directoryIterator = new DirectoryIterator($directory);
        $iterator = new FilenameFilter($directoryIterator, '/.*\.src/');

        foreach ($iterator as $fileInfo) {
            $testCase = new TestCase($directory, $fileInfo->getBasename('.src'));
            array_push($testCases, $testCase);
        }
        return $testCases;
    }
}

class PreprocessTestSuiteReader implements ITestSuiteReader
{
    private $testSuiteReader;

    public function __construct(ITestSuiteReader $reader) {
        $this->testSuiteReader = $reader;
    }

    public function read() {
        $testSuites = $this->testSuiteReader->read();

        foreach ($testSuites as $testSuite) {
            $dir = $testSuite->getDirectory();

            foreach ($testSuite->getTestCases() as $testCase) {
                // create empty in and out files if they don't exist
                $testCasePath = $dir."/".$testCase->getName();
                $inFilePath = $testCasePath . ".in";
                $outFilePath = $testCasePath . ".out";
                $rcFilePath = $testCasePath . ".rc";
                if (!file_exists($inFilePath)) {
                    $handle = fopen($inFilePath, 'w');
                    if (!$handle)
                        throw new Exception("Couldn't create file " . $inFilePath, Errors::OPEN_INPUT_FILE_ERROR);
                    fclose($handle);
                }
                if (!file_exists($outFilePath)) {
                    $handle = fopen($outFilePath, 'w');
                    if (!$handle)
                        throw new Exception("Couldn't create file " . $outFilePath, Errors::OPEN_OUTPUT_FILE_ERROR);
                    fclose($handle);
                }
                // create rc file with "0" if it doesn't exist
                if (!file_exists($rcFilePath)) {
                    $handle = fopen($rcFilePath, 'w');
                    if (!$handle)
                        throw new Exception("Couldn't create file " . $rcFilePath, Errors::OPEN_INPUT_FILE_ERROR);
                    fwrite($handle, "0");
                    fclose($handle);
                }
            }
        }
        return $testSuites;
    }
}

class HtmlSummaryGenerator implements ISummaryGenerator
{
    public function generate($testSuiteResults) {
        $this->generateHeader();
        $this->generateTestSuiteBlocks();

        // foreach ($testSuiteResults as $testSuiteResult) {
        //     echo "TestSuite \"{$testSuiteResult->getTestSuite()->getDirectory()}\"\n";
        //     echo "Passed: {$testSuiteResult->getTotalPassed()}\n";
        //     echo "Failed: {$testSuiteResult->getTotalFailed()}\n";
        // }
    }

    private function generateHeader() {

    }

    private function generateTestSuiteBlocks() {
        foreach ($testSuiteResults as $testSuiteResult) {
            $this->generateTestSuiteBlock($testSuiteResult);
        }
    }

    private function generateTestSuiteBlock(TestSuiteResult $testSuiteResult) {
        $this->generateTestCasesDetails();
        $this->generateTestSuiteBlockSummary();
    }

    private function generateTestCasesDetails() {
        
    }

    private function generateTestSuiteBlockSummary() {
        
    }
}

class TestRunner implements ITestRunner
{
    private $parseScript;
    private $parseOnly;
    private $intScript;
    private $intOnly;
    private $directory;

    public function __construct($parseScript, $parseOnly, $intScript, $intOnly) {
        $this->parseScript = $parseScript;
        $this->parseOnly = $parseOnly;
        $this->intScript = $intScript;
        $this->intOnly = $intOnly;
    }

    public function runTestSuite(TestSuite $testSuite) {
        $testCaseResults = array();
        $this->directory = $testSuite->getDirectory();

        foreach ($testSuite->getTestCases() as $testCase) {
            $testCaseResult = $this->runTest($testCase);
            array_push($testCaseResults, $testCaseResult);
        }
        return new TestSuiteResult($testSuite, $testCaseResults);
    }

    public function runTest(TestCase $test) {
        error_log("Running test {$test->getName()}");
        if ($this->parseOnly) {
            return $this->testParseOnly($test);
        }
        else if ($this->intOnly) {
            return $this->testInterpretOnly($test);
        }
        else {
            throw new Exception("Unimplemented exception");
        }
    }

    private function testParseOnly(TestCase $testCase) {
        $tempOutFilename = tempnam($this->directory, "parserOut");

        // run parser
        $parseCommand = $this->getParseCommand($testCase, $tempOutFilename);
        exec($parseCommand, $output, $returnCode);

        $hasPassed = $this->checkReturnCode($testCase, $returnCode);

        if ($hasPassed && $returnCode == 0) {
            # run JExamlXml
        }
        unlink($tempOutFilename);
        return new TestCaseResult($testCase, $hasPassed);
    }

    private function checkReturnCode(TestCase $testCase, $returnCode) {
        $rcFilename =  $testCase->getReturnCodeFilename();
        $expectedReturnCode = file_get_contents($rcFilename);
        return $returnCode == $expectedReturnCode;    
    }

    private function testInterpretOnly(TestCase $testCase) {
        $tempOutFilename = tempnam($this->directory, "interpretOut"); // duplicated

        // run interpret
        $parseCommand = $this->getInterpretCommand($testCase, $tempOutFilename);
        exec($parseCommand, $output, $returnCode);

        // check return code

        // diff results
        
        unlink($tempOutFilename); // duplicaed
        return new TestCaseResult($testCase, false); // duplicated
    }
    
    private function getParseCommand($test, $tmpOutFilename) {
        $srcFile =  $test->getSourceFilename();
        return "D:\\Programs\\Xampp\\php\\php.exe -f {$this->parseScript} < \"{$srcFile}\" > \"{$tmpOutFilename}\"";
    }

    private function getInterpretCommand($test, $tmpOutFilename) {

    }
}


try {
    $argsParser = new ArgsParser($argv);
    $args = $argsParser->parse();
    
    $testRunner = new TestRunner($args->parseScript, $args->parseOnly, $args->intScript, $args->intOnly);
    $testSuiteReader = new DirectoryTestSuiteReader($args->directory, $args->recursive);
    $testSuiteReader = new PreprocessTestSuiteReader($testSuiteReader);
    $summaryGenerator = new HtmlSummaryGenerator();

    $testSuites = $testSuiteReader->read();

    $testSuiteResults = array();
    foreach ($testSuites as $testSuite) {
        $testSuiteResult = $testRunner->runTestSuite($testSuite);
        array_push($testSuiteResults, $testSuiteResult);
    }

    $summaryGenerator->generate($testSuiteResults);    
}
catch (Exception $e) {
    error_log($e->getMessage());
    exit($e->getCode());
}


?>