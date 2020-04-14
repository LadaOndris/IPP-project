<?php

interface ITestSuiteReader
{
    public function read($directory, $regex, $recursively); // returns a set of testsuites
}


class TestfileTestSuiteReader implements ITestSuiteReader
{
    private $directorySuiteReader;
    private $testSuites = array();

    public function __construct($directorySuiteReader) {
        $this->directorySuiteReader = $directorySuiteReader;
    }

    public function read($testfile, $recursively, $regex) {
        $this->testfile = $testfile;
        $this->regex = $regex;

        $this->loadFile();
        foreach ($this->directories as $directory) {
            $testSuites = $this->directorySuiteReader->read($directory, $recursively, $regex);
            $this->appendTestSuites($testSuites);
        }
        foreach ($this->files as $file) {
            $dirname = dirname($file);
            $filenameWithoutExtension = basename($file, ".src");
            $testSuites = $this->directorySuiteReader->read($dirname, false, $filenameWithoutExtension);
            $this->appendTestSuites($testSuites);
        }
        return $this->testSuites;
    }

    private function loadFile() {
        $this->directories = array();
        $this->files = array();

        foreach ($this->testfile as $line) {
            $line = trim($line);
            if ($line == '') // ignore empty lines
                continue;
            $pathParts = pathinfo($line);
            
            if ($this->directoryExists($line)) {
                array_push($this->directories, $line);
            }
            else if ($this->fileExists($line) && strtolower($pathParts['extension']) == 'src') {
                array_push($this->files, $line);
            }
            else {
                throw new Exception("Bad file or directory: " . $line, Errors::OPEN_INPUT_FILE_ERROR);
            }
        }
    }

    private function fileExists($file) {
        return file_exists($file) and !is_dir($file);
    }

    private function directoryExists($directory) {
        return file_exists($directory) and is_dir($directory);
    }

    private function appendTestSuites($testSuites) {
        foreach ($testSuites as $testSuite) {
            array_push($this->testSuites, $testSuite);
        }
    }
}

class DirectoryTestSuiteReader implements ITestSuiteReader
{
    public function read($directory, $recursively, $regex) {
        $directory = rtrim($directory, "/\\"); // remove ending slash and backslash
        $this->directory = $directory;
        $this->regex = $regex;
        $this->recursively = $recursively;
        
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

    public function read($directory, $recursively, $regex) {
        $testSuites = $this->testSuiteReader->read($directory, $recursively, $regex);

        foreach ($testSuites as $testSuite) {
            $dir = $testSuite->getDirectory();
            $dir = rtrim($dir, "/\\"); // remove ending slash and backslash

            foreach ($testSuite->getTestCases() as $testCase) {
                // create empty in and out files if they don't exist
                $testCasePath = $dir.DIRECTORY_SEPARATOR.$testCase->getName();
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