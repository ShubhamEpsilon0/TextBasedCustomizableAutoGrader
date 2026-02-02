# autograder/script_runner/PythonTestRunner.py
from autograder.script_runner.TestRunner import TestRunner
from autograder.logging.Logger import Logger

import subprocess
from typing import Optional, Union, List
import sys
import os

class PythonTestRunner(TestRunner):
    """
    Runs Python scripts/functions for testing.
    Supports input from string, list, or file.
    Can run standalone scripts or poetry package commands.
    """
    def __init__(self, logger: Logger, buildScript: Optional[str], fatalErrors: List[str], placeholderRegex: Optional[dict] = None):
        # buildScript is not relevant for Python
        super().__init__(logger, buildScript, fatalErrors, placeholderRegex)
        self.component = "PythonTestRunner"

    def build(self, studentSubmissionPath: str, buildScriptOverride: Optional[str] = None):
        # Python generally doesn't require build
        return True, "", ""

    def run(
        self,
        studentSubmissionPath: str,
        testFolderPath: str,
        inputData: Optional[Union[str, List[str]]] = None,
        expectedOutputFile: Optional[str] = None,
        runScriptPath: Optional[str] = None,
        timeout: int = 120
    ) -> dict:
        script = runScriptPath
        if not script:
            self.logger.error(self._log_template({
                "StudentSubmissionPath": studentSubmissionPath,
                "RunScript": "",
                "Error": "No Python test script provided"
            }))
            raise ValueError("No Python test script provided")

        # Handle input
        if isinstance(inputData, str):
            args = inputData.strip().split()
        elif isinstance(inputData, list):
            args = inputData
        else:
            args = []

        try:
            interpreterPath = self._resolve_python_interpreter(testFolderPath)
            cmd = [interpreterPath, script, studentSubmissionPath, *args]
            # # If using poetry run
            # if script.endswith(".py"):
                
            # else:
            #     # Assume poetry package command
            #     cmd = ["poetry", "run", script, studentSubmissionPath, *args]

            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                text=True,
            )


            output = result.stdout.strip()
            error = result.stderr.strip()

            # Fatal errors detection
            self.detectFatalErrors([output, error])

            return self.generateTestResults(output, error, expectedOutputFile)

        except subprocess.TimeoutExpired:
            self.logger.error(self._log_template({
                "StudentSubmissionPath": studentSubmissionPath,
                "RunScript": script,
                "Error": "TimeoutExpired"
            }))
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
            self.logger.error(self._log_template({
                "StudentSubmissionPath": studentSubmissionPath,
                "RunScript": script,
                "Error": str(e)
            }))
            self.detectFatalErrors([str(e)])
            return {
                "passed": False,
                "output": "",
                "expected": "",
                "error": f"Unexpected error: {str(e)}",
                "similarity_report": []
            }

    def _resolve_python_interpreter(self, workingDir: str) -> str:
        """
        If .venv exists, use its python interpreter.
        Otherwise fallback to sys.executable.
        """
        venv_path = os.path.join(workingDir, ".venv")

        if os.path.isdir(venv_path):
            if os.name == "nt":
                python_path = os.path.join(venv_path, "Scripts", "python.exe")
            else:
                python_path = os.path.join(venv_path, "bin", "python")

            if os.path.isfile(python_path):
                return python_path

        return sys.executable