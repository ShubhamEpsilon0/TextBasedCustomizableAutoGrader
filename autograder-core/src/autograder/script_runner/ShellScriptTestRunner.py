from autograder.script_runner.TestRunner import TestRunner
import subprocess
import os
import json
from typing import Optional, Union, List

class ShellScriptTestRunner(TestRunner):
    """
    Executes build and run scripts for C assignments.
    Supports global project-level scripts and per-test overrides.
    """
    def __init__(self, buildScript, fatalErrors: List[str], placeholderRegex: Optional[dict] = None):
        super().__init__(buildScript, fatalErrors, placeholderRegex)

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------
    def build(self, studentSubmissionPath: str, buildScriptOverride: Optional[str] = None):
        """
        Builds a student submission using the provided build script.
        If no build script is provided, it assumes build success.
        """
        script = buildScriptOverride or self.buildScript
        if not script:
            return True, "", ""
        
        try:
            result = subprocess.run(
                [script, studentSubmissionPath],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
                text=True
            )

            output = result.stdout.strip()
            error = result.stderr.strip()

            # Fatal errors detection
            self.detectFatalErrors([output, error])

            return result.returncode == 0, output, error

        except subprocess.SubprocessError as e:
            return False, None, str(e)

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------
    def run(
        self,
        studentSubmissionPath: str,
        testFolderPath: str,
        inputData: Optional[Union[str, List[str]]] = None,
        expectedOutputFile: Optional[str] = None,
        runScript: Optional[str] = None,
        timeout: int = 120
    ) -> dict:
        """
        Runs a single test on the student submission.
        inputData can be:
        - a string (will be split into arguments)
        - a list of strings
        - None (no input arguments)
        """
        script = runScript
        if not script:
            raise ValueError("No run script provided")

        # Prepare input arguments
        if inputData is None:
            args = []
        elif isinstance(inputData, str):
            args = inputData.strip().split()
        else:
            args = inputData

        try:
            result = subprocess.run(
                [script, studentSubmissionPath, *args],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                text=True
            )

            output = result.stdout.strip()
            error = result.stderr.strip()

            # Fatal errors detection
            self.detectFatalErrors([output, error])

            # Generate test report
            return self.generateTestResults(output, error, expectedOutputFile)

        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "output": "",
                "expected": "",
                "error": "Timeout: student code took too long",
                "similarity_report": []
            }
        except Exception as e:
            # Fatal errors in exception
            # Fatal errors detection
            self.detectFatalErrors([str(e)])
            return {
                "passed": False,
                "output": "",
                "expected": "",
                "error": f"Unexpected error: {str(e)}",
                "similarity_report": []
            }
