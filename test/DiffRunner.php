<?php

class DiffRunner {

    public function __construct($printDebugInfo) {
        $this->printDebugInfo = $printDebugInfo;
    }

    public function run(TestCase $testCase, $file1, $file2) {
        $this->file1 = $file1;
        $this->file2 = $file2;
        $this->testCase = $testCase;
        $this->runDiffCommand();
        $this->checkReturnCode();
        $this->printInfo();
        return $this->hasPassed;
    }

    private function runDiffCommand() {
        $diffCommand = $this->getDiffCommand();
        system($diffCommand, $diffReturnCode);
        $this->returnCode = $diffReturnCode;
    }

    private function getDiffCommand() {
        return "diff \"{$this->file1}\" \"{$this->file2}\" 2> /dev/null > /dev/null";
    }

    private function checkReturnCode() {
        $this->hasPassed = $this->returnCode == 0;
    }

    private function printInfo() {
        if ($this->printDebugInfo && !$this->hasPassed) {
            $content1 = urlencode(file_get_contents($this->file1));
            $content2 = urlencode(file_get_contents($this->file2));
            error_log("Diff failed, return code: {$this->returnCode}");
            error_log("First output:\n{$content1}");
            error_log("Second output:\n{$content2}");
        }
    }
}

?>