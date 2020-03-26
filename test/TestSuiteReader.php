<?php

interface ITestSuiteReader
{
    public function read(); // returns a set of testsuites
}


class DirectoryTestSuiteReader implements ITestSuiteReader
{
    private $directory;
    private $recursively;
    private $regex = ".*";

    public function __construct($directory, $recursively, $regex) {
        $this->directory = $directory;
        $this->recursively = $recursively;
        $this->regex = $regex;
    }

    public function read() {
        $testSuites = array();
        $dirs = array();
        if ($this->recursively) {
            $dirs = $this->getSubDirectories($this->directory);
        }
        array_push($dirs, $this->directory);

        foreach ($dirs as $dir) {
            $testCases = $this->getTestCases($dir);
            $testSuite = new TestSuite($dir, $testCases);
            array_push($testSuites, $testSuite);
        }
        return $testSuites;
    }

    private function getSubDirectories($directory) {
        $dirs = array();
        $files = scandir($directory);
        foreach ($files as $file) {
            $dirPath = $directory . DIRECTORY_SEPARATOR . $file;
            
            if (is_dir($dirPath)) {
                if (basename($dirPath) == "." || basename($dirPath) == "..")
                    continue;
                array_push($dirs, $dirPath);

                $dirsRecursive = $this->getSubDirectories($dirPath);
                $dirs = array_merge($dirsRecursive, $dirs);
            }
        }
        return $dirs;
    }

    private function getTestCases($directory) {
        $testCases = array();
        $directoryIterator = new DirectoryIterator($directory);
        $iterator = new FilenameFilter($directoryIterator, "/{$this->regex}\.src/");

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

?>