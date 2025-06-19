from autograder.scripts.TestRunner import TestRunner

import subprocess
import time

class ShellScriptTestRunner(TestRunner):
    def __init__(self, buildScript, runScript, fatalErrors):
        super().__init__(buildScript, runScript, fatalErrors)

    def build(self, studentSubmissionPath):
        if not self.buildScript:
            return True, "", ""

        try:
            result = subprocess.run(
                [self.buildScript, studentSubmissionPath],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
                text=True
            )
            output = result.stdout.strip()
            error = result.stderr.strip()


            for fatal in self.fatalErrors:
                if fatal.lower() in output.lower() or fatal.lower() in error.lower():
                    print(f"🔥 Fatal Error Detected: '{fatal}' in output.")
                    raise SystemExit(f"Autograder terminated due to fatal error: {fatal}")
                
            return result.returncode == 0, output, error
        except subprocess.SubprocessError as e:
            return False, None, str(e)

    def run(self, inputStr: str, expectedOutputFilePath: str, studentSubmissionPath: str, timeout:int = 120) -> dict:
        output, error = None, None
        try:
            test_input = inputStr.strip().split()

            #print("Test Started with timeout = ", timeout)
            #start = time.time()
            result = subprocess.run(
                [self.runScript, studentSubmissionPath, *test_input],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                text=True,
            )
            #end = time.time()
            #print("Test ", inputStr ," Concluded.. Took ", end - start, " seconds")

            output = result.stdout.strip()
            error = result.stderr.strip()


            for fatal in self.fatalErrors:
                if (output and fatal.lower() in output.lower()) or (error and fatal.lower() in error.lower()):
                    print(f"🔥 Fatal Error Detected: '{fatal}' in output.")
                    raise SystemExit(f"Autograder terminated due to fatal error: {fatal}")

            # print("generating Report")
            return self.generateTestResults(output, error, expectedOutputFilePath)

        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "output": "",
                "expected": "",
                "error": "Timeout: student code took too long",
                "similarity_report": []
            }

        except Exception as e:
            # print(e)

            for fatal in self.fatalErrors:
                if (fatal.lower() in str(e).lower()):
                    print(f"🔥 Fatal Error Detected: '{fatal}' in output.")
                    raise SystemExit(f"Autograder terminated due to fatal error: {fatal}")

            return {
                "passed": False,
                "output": "",
                "expected": "",
                "error": f"Unexpected error: {str(e)}",
                "similarity_report": []
            } 
