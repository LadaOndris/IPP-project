<?php

class ParseRunner {
    
    public function __construct($parseScript, $debugInfo = False) {
        $this->parseScript = $parseScript;
        $this->debugInfo = $debugInfo;
    }

    /**
     * Runs a single test case using parser script.
     */
    public function run(TestCase $testCase, $sourceFilename, $outputFilename, $printDebugInfo = False) {
        $this->testCase = $testCase;
        $this->sourceFilename = $sourceFilename;
        $this->outputFilename = $outputFilename;
        $this->debugInfo = $printDebugInfo;
        $this->runParse();
        $this->checkReturnCode();
        $this->printDebugInfo();
        return $this->hasPassed;
    }

    private function runParse() {
        $parseCommand = $this->getParseCommand();
        system($parseCommand, $returnCode);
        $this->returnCode = $returnCode;
    }
    
    private function getParseCommand() {
        $srcFilename =  $this->testCase->getSourceFilename();
        $actualOutputFilename = $this->testCase->getActualOutputFilename();

        return "php7.4 \"{$this->parseScript}\" < \"{$srcFilename}\" > \"{$actualOutputFilename}\" ";
    }

    private function checkReturnCode() {
        $this->hasPassed = $this->returnCode == $this->getExpectedReturnCode($this->testCase);    
    }

    private function getExpectedReturnCode(TestCase $testCase) {
        $rcFilename =  $testCase->getReturnCodeFilename();
        return file_get_contents($rcFilename);
    }

    private function printDebugInfo() {
        if (!$this->hasPassed && $this->debugInfo) {
            $actualOutputFilename = $this->testCase->getActualOutputFilename();
            $output = file_get_contents($actualOutputFilename);
            $expectedRc = $this->getExpectedReturnCode($this->testCase);
            error_log("parse.php return code: {$this->returnCode}, expected: {$expectedRc}");
            error_log("parse.php output: \n{$output}");
        }
    }

    public function isInputValid() {
        return $this->hasPassed && $this->returnCode == 0;
    }
}

?>