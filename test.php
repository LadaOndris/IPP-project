<?php

require_once("test/TestRunner.php");
require_once("test/ParseRunner.php");
require_once("test/InterpretRunner.php");
require_once("test/XmlDiffRunner.php");
require_once("test/DiffRunner.php");
require_once("test/TestCase.php");
require_once("test/HtmlSummaryGenerator.php");
require_once("test/TestSuiteReader.php");
require_once("test/ArgsParser.php");

class Errors
{
    const INVALID_COMBINATION_OF_PARAMS = 10;
    const INVALID_ARGUMENT = 10;
    const OPEN_INPUT_FILE_ERROR = 11;
    const OPEN_OUTPUT_FILE_ERROR = 12;
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

    public function getTestCaseResults() {
        return $this->testCaseResults;
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

function printHelp() {
    echo "test.php help:\n";
    echo "--help                        Prints this help.\n";
    echo "--verbose                     Prints information about failed tests.\n";
    echo "--directory PATH              Set the directory containing tests. Default is current.\n";
    echo "--recursive                   Search tests directory recursively.\n";
    echo "--parse-script PATH           Set path to parse.php script, default is ./parse.php.\n";
    echo "--int-script PATH             Set path to interpret.py script, default is ./interpret.py.\n";
    echo "--int-only                    Run interpret only.\n";
    echo "--parse-only                  Run parse script only.\n";
    echo "--jexamxml PATH               Set path to jexamxml.jar script for xml comparison, default is /pub/courses/ipp/jexamxml/jexamxml.jar.\n";
}

try {
    $argsParser = new ArgsParser($argv);
    $args = $argsParser->parse();
    
    $parseRunner = new ParseRunner($args->parseScript, $args->verbose);
    $xmlDiffRunner = new XmlDiffRunner($args->jexamxml, $args->verbose);
    $interpretRunner = new InterpretRunner($args->intScript, $args->verbose);
    $outputDiffRunner = new DiffRunner($args->verbose);
    $testRunner = new TestRunner($parseRunner, $args->parseOnly, $interpretRunner, $args->intOnly, 
                                 $xmlDiffRunner, $outputDiffRunner, $args->verbose);
    $testSuiteReader = new DirectoryTestSuiteReader($args->directory, $args->recursive);
    $testSuiteReader = new PreprocessTestSuiteReader($testSuiteReader);
    $summaryGenerator = new HtmlSummaryGenerator();

    if ($args->help) {
        printHelp();
    }
    else {
        $testSuites = $testSuiteReader->read();

        $testSuiteResults = array();
        foreach ($testSuites as $testSuite) {
            $testSuiteResult = $testRunner->runTestSuite($testSuite);
            array_push($testSuiteResults, $testSuiteResult);
        }

        $summaryGenerator->generate($testSuiteResults);   
    } 
}
catch (Exception $e) {
    error_log($e->getMessage());
    exit($e->getCode());
}


?>