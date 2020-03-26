<?php

class InterpretRunner {

    public function __construct($interpretScript, $printDebugInfo) {
        $this->interpretScript = $interpretScript;
        $this->printDebugInfo = $printDebugInfo;
    }

    public function run(TestCase $testCase, $sourceFilename, $inputFilename, $outputFilename) {
        $this->testCase = $testCase;
        $this->sourceFilename = $sourceFilename;
        $this->inputFilename = $inputFilename;
        $this->outputFilename = $outputFilename;

        $this->runInterpretCommand();
        $this->checkReturnCode();
        $this->printDebugInfo();
        return $this->hasPassed;
    }

    private function runInterpretCommand() {
        $parseCommand = $this->getInterpretCommand();
        system($parseCommand, $returnCode);
        $this->returnCode = $returnCode;
    }

    private function checkReturnCode() {
        $this->hasPassed = $this->returnCode == $this->getExpectedReturnCode($this->testCase);    
    }

    private function getExpectedReturnCode(TestCase $testCase) {
        $rcFilename =  $testCase->getReturnCodeFilename();
        return file_get_contents($rcFilename);
    }

    private function getInterpretCommand() {
        return "python3.8 \"{$this->interpretScript}\" --source=\"{$this->sourceFilename}\" --input=\"{$this->inputFilename}\" > \"{$this->outputFilename}\" ";
    }

    private function printDebugInfo() {
        if (!$this->hasPassed) {
            error_log("Interpret return code: {$this->returnCode}");
            error_log("Expected return code: {$this->getExpectedReturnCode($this->testCase)}");
        }
    }

    public function isInputValid() {
        return $this->hasPassed && $this->returnCode == 0;
    }
    
}


?>