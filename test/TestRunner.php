<?php

class TestRunner implements ITestRunner
{
    public function __construct($parseRunner, $parseOnly, $interpretRunner, $intOnly, $xmlDiffRunner, $outputDiffRunner, $verbose) {
        $this->parseRunner = $parseRunner;
        $this->parseOnly = $parseOnly;
        $this->interpretRunner = $interpretRunner;
        $this->intOnly = $intOnly;
        $this->xmlDiffRunner = $xmlDiffRunner;
        $this->outputDiffRunner = $outputDiffRunner;
        $this->verbose = $verbose;
    }

    public function runTestSuite(TestSuite $testSuite) {
        $testCaseResults = array();

        foreach ($testSuite->getTestCases() as $testCase) {
            $testCaseResult = $this->runTest($testCase);
            array_push($testCaseResults, $testCaseResult);
        }
        return new TestSuiteResult($testSuite, $testCaseResults);
    }

    public function runTest(TestCase $test) {
        if ($this->verbose)
            error_log("Running test {$test->getPathname()}");
            
        if ($this->parseOnly) {
            return $this->testParse($test);
        }
        else if ($this->intOnly) {
            return $this->testInterpret($test);
        }
        else {
            return $this->testBoth($test);
        }

        if ($this->verbose)
            error_log("\n");
    }

    private function testParse(TestCase $testCase) {
        $sourceFilename = $testCase->getSourceFilename();
        $expectedOutputFilename = $testCase->getOutputFilename();
        $actualOutputFilename = $testCase->getActualOutputFilename();

        $hasPassed = $this->parseRunner->run($testCase, $sourceFilename, $actualOutputFilename, true);
        if ($this->parseRunner->isInputValid()) {
            $hasPassed = $this->xmlDiffRunner->run($testCase, $expectedOutputFilename, $actualOutputFilename);
        }
        return new TestCaseResult($testCase, $hasPassed);
    }

    private function testInterpret(TestCase $testCase) {
        $sourceFilename = $testCase->getSourceFilename();
        $inputFilename = $testCase->getInputFilename();
        $expectedOutputFilename = $testCase->getOutputFilename();
        $actualOutputFilename = $testCase->getActualOutputFilename();


        $hasPassed = $this->interpretRunner->run($testCase, $sourceFilename, $inputFilename, $actualOutputFilename);
        if ($this->interpretRunner->isInputValid()) {
            $hasPassed = $this->outputDiffRunner->run($testCase, $expectedOutputFilename, $actualOutputFilename);
        }
        return new TestCaseResult($testCase, $hasPassed);
    }

    private function testBoth(TestCase $testCase) {
        $sourceFilename = $testCase->getSourceFilename();
        $inputFilename = $testCase->getInputFilename();
        $expectedOutputFilename = $testCase->getOutputFilename();
        $actualOutputFilename = $testCase->getActualOutputFilename();

        $this->parseRunner->run($testCase, $sourceFilename, $actualOutputFilename);
        if ($this->parseRunner->returnCode == 0) {
            $interpretOutputFilename = tempnam($testCase->getPath(), $testCase->getName() . ".tmp");

            $hasPassed = $this->interpretRunner->run($testCase, $actualOutputFilename, $inputFilename, $interpretOutputFilename);
            if ($this->interpretRunner->isInputValid()) {
                $hasPassed = $this->outputDiffRunner->run($testCase, $expectedOutputFilename, $interpretOutputFilename);
            }
            
            unlink($interpretOutputFilename);
            return new TestCaseResult($testCase, $hasPassed);
        }
        else {
            return new TestCaseResult($testCase, $this->parseRunner->hasPassed);
        }
    }
}

?>