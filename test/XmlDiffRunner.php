<?php

class XmlDiffRunner {

    public function __construct($jexamxmlFilename, $printDebugInfo) {
        $this->jexamxmlFilename = $jexamxmlFilename;
        $this->printDebugInfo = $printDebugInfo;
    }

    public function run(TestCase $testCase, $xmlFile1, $xmlFile2) {
        $this->xmlFile1 = $xmlFile1;
        $this->xmlFile2 = $xmlFile2;
        $this->testCase = $testCase;
        $this->runXmlCommand();
        $this->checkReturnCode();
        $this->printDebugInfo();
        return $this->hasPassed;
    }

    private function runXmlCommand() {
        $xmlDifCommand = $this->getJexamxmlCommand();
        system($xmlDifCommand, $xmlDifReturnCode);
        $this->returnCode = $xmlDifReturnCode;
    }

    private function getJexamxmlCommand() {
        return "java -jar \"{$this->jexamxmlFilename}\" \"{$this->xmlFile1}\" \"{$this->xmlFile2}\" 2> /dev/null > /dev/null";
    }

    private function checkReturnCode() {
        $this->hasPassed = $this->returnCode == 0;
    }

    private function printDebugInfo() {
        if (!$this->hasPassed && $this->printDebugInfo) {
            $content1 = file_get_contents($this->xmlFile1);
            $content2 = file_get_contents($this->xmlFile2);
            error_log("jexamxml return code: {$this->returnCode}, expected: 0");
            error_log("Xml file 1: \n{$content1}");
            error_log("Xml file 2: \n{$content2}");
        }
    }

}

?>