# autograder/script_runner/TestRunner.py

from abc import ABC, abstractmethod
from typing import Optional, Union, List, Dict
import difflib
import os

from autograder.utils.ExpectedOutputMatcher import ExpectedOutputMatcher

class TestRunner(ABC):
    """
    Base class for all test runners.
    """

    def __init__(
        self,
        buildScript: Optional[str] = None,
        fatalErrors: Optional[List[str]] = None,
        placeholderRegex: Dict[str, str] | None = None
    ):
        self.buildScript = buildScript
        self.fatalErrors = fatalErrors or []
        self.placeholderRegex = placeholderRegex or {}

    # -----------------------------------------------------------
    # Lifecycle hooks
    # -----------------------------------------------------------
    @abstractmethod
    def build(
        self,
        studentSubmissionPath: str,
        buildScriptOverride: Optional[str] = None
    ) -> tuple[bool, str, str]:
        """
        Returns:
            success (bool), stdout (str), stderr (str)
        """
        pass

    @abstractmethod
    def run(
        self,
        studentSubmissionPath: str,
        testFolderPath: str,
        inputData: Optional[Union[str, List[str]]] = None,
        expectedOutputFile: Optional[str] = None,
        runScript: Optional[str] = None,
        timeout: int = 120
    ) -> Dict:
        pass

    # -----------------------------------------------------------
    # Shared utilities
    # -----------------------------------------------------------
    def detectFatalErrors(self, outputs: list[str]):
        """
        Scan outputs for fatal error keywords.
        """
        for fatal in self.fatalErrors:
            for out in outputs:
                if out and fatal.lower() in out.lower():
                    raise SystemExit(
                        f"Autograder terminated due to fatal error: {fatal}"
                    )

    def generateTestResults(
        self,
        actualOutput: str,
        errorOutput: str,
        expectedOutputFile: str,
    ) -> Dict:
        """
        Compare output with expected output (if provided).
        """
        expected = ""
        passed = True
        similarity_report = []
        if not os.path.exists(expectedOutputFile):
            return {
                "passed": False,
                "output": actualOutput,
                "expected": "",
                "error": f"Expected output file not found: {expectedOutputFile}",
                "similarity_report": []
            }

        with open(expectedOutputFile, "r", encoding="utf-8") as f:
            expected = f.read().strip()

        actualLines = [l.strip() for l in actualOutput.splitlines()]
        expectedLines = [l.strip() for l in expected.splitlines()]

        matcher = ExpectedOutputMatcher(self.placeholderRegex)
        passed = matcher.match(expectedLines, actualLines)

        similarity_report = []
        if not passed and len(expectedLines) <= 100:
            similarity_report = self.computeSimilarityReport(
                expectedLines, actualLines
            )

        return {
            "passed": passed,
            "output": actualOutput if not passed else "",
            "expected": expected,
            "error": errorOutput,
            "similarity_report": similarity_report
        }

    # -----------------------------------------------------------
    # Helper methods (optional but recommended)
    # -----------------------------------------------------------
    def normalizeInput(self, inputData: Optional[Union[str, List[str]]]) -> List[str]:
        if inputData is None:
            return []
        if isinstance(inputData, list):
            return inputData
        return inputData.strip().split()

    def computeSimilarityReport(self, expected_lines, actual_lines):
        similarity_report = []
        for expected in expected_lines:
            best_match = None
            best_score = 0
            for actual in actual_lines:
                score = difflib.SequenceMatcher(None, expected, actual).ratio()
                if score > best_score:
                    best_score = score
                    best_match = actual
            similarity_report.append({
                "expected_line": expected,
                "closest_line": best_match
            })
        return tuple(similarity_report)
