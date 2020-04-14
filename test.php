<?php
require_once("test/ParseRunner.php");
require_once("test/TestRunner.php");
require_once("test/InterpretRunner.php");
require_once("test/XmlDiffRunner.php");
require_once("test/DiffRunner.php");
require_once("test/TestCase.php");
require_once("test/HtmlSummaryGenerator.php");
require_once("test/TestSuiteReader.php");
require_once("test/ArgsParser.php");

/**
 * Definition of error codes for possible errors.
 */
class Errors
{
    const INVALID_COMBINATION_OF_PARAMS = 10;
    const INVALID_ARGUMENT = 10;
    const OPEN_INPUT_FILE_ERROR = 11;
    const OPEN_OUTPUT_FILE_ERROR = 12;
}

/**
 * TestCaseResult contains the result of a single TestCase.
 */
class TestCaseResult
{
    public function __construct(TestCase $testCase, $hasPassed) {
        $this->testCase = $testCase;
        $this->hasPassed = $hasPassed;
    }

    /**
     * Returns true if TestCase passed.
     */
    public function hasPassed() {
        return $this->hasPassed;
    }

    /**
     * Returns a TestCase of this TestCaseResult.
     */
    public function getTestCase() {
        return $this->testCase;
    }
}

/**
 * TestSuiteResult contains the test results of TestSuite.
 */
class TestSuiteResult
{
    /**
     * testSuite The target TestSuite
     * testCaseResult An array of instances of TestCaseResult class.
     */
    public function __construct(TestSuite $testSuite, $testCaseResults) {
        $this->testSuite = $testSuite;
        $this->testCaseResults = $testCaseResults;
    }

    /**
     * Returns the total number of passed test cases.
     */
    public function getTotalPassed() {
        $totalPassed = 0;
        foreach ($this->testCaseResults as $testCaseResult) {
            if ($testCaseResult->hasPassed()) {
                $totalPassed++;
            }
        }
        return $totalPassed;
    }

    
    /**
     * Returns the total number of failed test cases.
     */
    public function getTotalFailed() {
        return count($this->testCaseResults) - $this->getTotalPassed();
    }

    /**
     * Returns the test suite.
     */
    public function getTestSuite() {
        return $this->testSuite;
    }

    /**
     * Returns a TestCaseResult for each test in a TestSuite of this TestSuiteResult.
     */
    public function getTestCaseResults() {
        return $this->testCaseResults;
    }
}

/**
 * TestSuite represenets a set of tests. 
 * In this case it is a set of tests found in a single directory. 
 */
class TestSuite
{
    private $directory;
    private $testCases;
    
    public function __construct($directory, $testCases) {
        $this->directory = $directory;
        $this->testCases = $testCases;
    }
    
    /** 
     * Returns a directory of the test suite.
     * The test suite contains test from this directory.
     */
    public function getDirectory() {
        return $this->directory;
    }

    /**
     * Returns test cases.
     * These test cases are all located in a single directory.
     */
    public function getTestCases() {
        return $this->testCases;
    }
}

interface ITestRunner
{
    public function runTest(TestCase $test);
}

/**
 * Filters files from directory using a regex.
 */
class FilenameFilter extends FilterIterator 
{
    /**
     * it Base iterator
     * regex Regex to filter file names
     */
    public function __construct(Iterator $it, $regex) {
        $this->regex = $regex;
        parent::__construct($it);
    }

    /**
     * Overriden function of FilterIterator.
     * Accepts files which satisfy given regex.
     */
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
    echo "--match REGEX                 Regex to filter test names without extension and path.\n";
    echo "--testlist PATH               Set path to a file containing list of directories and files to test.\n";
}

try {
    /**
     *  Dependency injection entry point
     *  Initializes the object graph.
     */
    $argsParser = new ArgsParser($argv);
    $args = $argsParser->parse();

    $parseRunner = new ParseRunner($args->parseScript, $args->verbose);
    $xmlDiffRunner = new XmlDiffRunner($args->jexamxml, $args->verbose);
    $interpretRunner = new InterpretRunner($args->intScript, $args->verbose);
    $outputDiffRunner = new DiffRunner($args->verbose);
    $testRunner = new TestRunner($parseRunner, $args->parseOnly, $interpretRunner, $args->intOnly, 
                                 $xmlDiffRunner, $outputDiffRunner, $args->verbose);
    $testSuiteReader = new DirectoryTestSuiteReader();
    $testSuiteReader = new PreprocessTestSuiteReader($testSuiteReader);
    $testfileTestSuiteReader = new TestfileTestSuiteReader($testSuiteReader);
    $summaryGenerator = new HtmlSummaryGenerator();

    /**
     * Starts the whole test thing using the object graph that was built above.
     */
    if ($args->help) {
        printHelp();
    }
    else {
        /** Testlist is given */
        if (isset($args->testlist)) {
            $testlistfile = file($args->testlist);
            $testSuites = $testfileTestSuiteReader->read($testlistfile, $args->recursive, $args->match);
        }
        else { /** Directory is given */
            $testSuites = $testSuiteReader->read($args->directory, $args->recursive, $args->match);
        }
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