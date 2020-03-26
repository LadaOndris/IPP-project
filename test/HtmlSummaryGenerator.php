<?php

interface ISummaryGenerator
{
    public function generate($testSuiteResults);
}

class HtmlSummaryGenerator implements ISummaryGenerator
{
    private $testSuiteResults;

    public function generate($testSuiteResults) {
        $this->testSuiteResults = $testSuiteResults;
        $header = $this->generateHeader();
        $testSuiteBlocks = $this->generateTestSuiteBlocks();
        $html = $this->fillTemplate($header . $testSuiteBlocks);
        echo $html;
    }

    private function fillTemplate($content) {
        return 
        "<html>
            <head>
                <style>
                    body {    
                        max-width: 900px;
                        margin: auto;
                        font-family: \"Segoe UI\";
                    }

                    header {
                        display: flex;
                        justify-content: center;
                        flex-flow: column;
                        text-align: center;
                    }

                    #overallSummary {
                        display: flex;
                        justify-content: center;
                        width: inherit;
                        font-size: 28;
                        background: #c8e1e9;
                        border: 2px solid;
                        padding: 5px;
                    }

                    #overallSummary table {
                        width: 200px;
                        font-size: 20px;
                    }

                    .directorySummary table {
                        margin-top: 10px;
                        font-weight: bold;
                        font-size: 16px;
                    }

                    section table td {
                        width: 200px;
                    }

                    .failed {
                        color: red;
                    }

                    .passed {
                        color: green;
                    }
                </style>
            </head>
            <body>
                {$content}
            </body>
        </html>";
    }

    private function getTotalPassed() {
        $passed = 0;
        foreach ($this->testSuiteResults as $testSuiteResult) {
            $passed += $testSuiteResult->getTotalPassed();
        }
        return $passed;
    }

    private function getTotalFailed() {
        $failed = 0;
        foreach ($this->testSuiteResults as $testSuiteResult) {
            $failed += $testSuiteResult->getTotalFailed();
        }
        return $failed;
    }

    private function generateHeader() {
        $passed = $this->getTotalPassed();
        $failed = $this->getTotalFailed();
        $totalTests = $passed + $failed;
        return 
        "<header>
            <h1>Tests summary</h1>
            <div id=\"overallSummary\">
                <table>
                    <tr>
                        <td>Passed</td>
                        <td>{$passed}</td>
                    </tr>
                    <tr>
                        <td>Failed</td>
                        <td>{$failed}</td>
                    </tr>
                    <tr>
                        <td>Total</td>
                        <td>{$totalTests}</td>
                    </tr>
                </table>
            </div>
            <hr />
        </header>";
    }

    private function generateTestSuiteBlocks() {
        $testSuiteBlocks = "<section>";
        foreach ($this->testSuiteResults as $testSuiteResult) {
            $testSuiteBlocks .= $this->generateTestSuiteBlock($testSuiteResult);
        }
        return $testSuiteBlocks . "</section>";
    }

    private function generateTestSuiteBlock(TestSuiteResult $testSuiteResult) {
        $testCasesDetails = $this->generateTestCasesDetails($testSuiteResult);
        $testSuiteBlockSummary = $this->generateTestSuiteBlockSummary($testSuiteResult);
        return "<div class=\"testSuite\">" . $testCasesDetails . $testSuiteBlockSummary . "</div><hr />";
    }

    private function generateTestCasesDetails(TestSuiteResult $testSuiteResult) {
        $testCaseDetails = "<h2 class=\"directory\">{$testSuiteResult->getTestSuite()->getDirectory()}</h2><table>";

        foreach ($testSuiteResult->getTestCaseResults() as $testCaseResult) {
            $evaluation = $testCaseResult->hasPassed() ? "Passed" : "Failed";
            $testCaseDetails .= 
            "<tr>
                <td>{$testCaseResult->getTestCase()->getName()}</td>
                <td class=\"{$evaluation}\">{$evaluation}</td>
            </tr>";
        }
        return $testCaseDetails . "</table>";
    }

    private function generateTestSuiteBlockSummary(TestSuiteResult $testSuiteResult) {
        $passed = $testSuiteResult->getTotalPassed();
        $failed = $testSuiteResult->getTotalFailed();
        $total = $passed + $failed;

        return "<div class=\"directorySummary\">
                    <table>
                        <tr>
                            <td>Passed</td>
                            <td>{$passed}</td>
                        </tr>
                        <tr>
                            <td>Failed</td>
                            <td>{$failed}</td>
                        </tr>
                        <tr>
                            <td>Total</td>
                            <td>{$total}</td>
                        </tr>
                    </table>
                </div>";
    }
}

?>