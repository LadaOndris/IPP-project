<?php


class TestCase
{
    private $path;
    private $name;

    public function __construct($path, $name) {
        $this->path = $path;
        $this->name = $name;
    }

    public function getPath() {
        return $this->path;
    }

    public function getName() {
        return $this->name;
    }

    public function getPathname() {
        return $this->path . DIRECTORY_SEPARATOR . $this->name;
    }

    public function getSourceFilename() {
        return $this->getPathname() . ".src";
    }

    public function getInputFilename() {
        return $this->getPathname() . ".in";
    }
    
    public function getOutputFilename() {
        return $this->getPathname() . ".out";
    }

    public function getReturnCodeFilename() {
        return $this->getPathname() . ".rc";
    }

    public function getActualOutputFilename() {
        if (!isset($this->tempOutFilename))
            $this->tempOutFilename = tempnam($this->path, $this->name . ".tmp");
        return $this->tempOutFilename;
    }

    function __destruct() {
        if (isset($this->tempOutFilename))
            unlink($this->tempOutFilename);
    }
}

?>