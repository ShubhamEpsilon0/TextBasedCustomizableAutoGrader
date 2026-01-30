import difflib
import subprocess
import re
from typing import List

class TestRunner:
    PLACEHOLDER_REGEX = {
        "<PLACEHOLDER_ADDR>": r"\b(?:0x)?[0-9a-fA-F]{4,16}\b",
        "<PLACEHOLDER_UPTO_TEN_DIGIT_NUMBER>": r"\b[0-9]{1,10}\b"
    }
    def __init__(self, buildScript, runScript, fatalErrors):
        self.runScript = runScript
        self.fatalErrors: List[str] = fatalErrors
        self.buildScript = buildScript

    def build(self, studentSubmissionPath):
        raise NotImplementedError

    def run(self, input_str: str, expected_output_file: str, student_file: str, timeout:int)  -> dict:
        raise NotImplementedError
    
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
    
    def generateTestResults (self, output: str, error: str, expectedOutputFilePath: str):
            with open(expectedOutputFilePath, 'r') as f:
                expected = f.read().strip()

            output_lines = [line.strip() for line in output.splitlines()]
            expected_lines = expected.splitlines()

            formated_expected_lines = []
            for line in expected_lines:
                line = line.strip()
                line = line.replace("(",r"\(").replace(")",r"\)").replace("[",r"\[").replace("]",r"\]")
                for placeholder, pattern in TestRunner.PLACEHOLDER_REGEX.items():
                    line = line.replace(placeholder, pattern)
                line = ".*" + line +".*"
                formated_expected_lines.append(line)

            # print("start matching", len(output_lines),len(expected_lines))
            # exact_match = all(
            #     any(re.fullmatch(expected_pattern, actual_line) for actual_line in output_lines)
            #     for expected_pattern in formated_expected_lines
            # )

            compiled_patterns = [re.compile(p) for p in formated_expected_lines]

            # Store actual lines in a set to prevent redundant re.match calls
            output_lines_set = set(output_lines)

            # Check each pattern against all lines efficiently
            exact_match = all(
                any(pattern.fullmatch(line) for line in output_lines_set)
                for pattern in compiled_patterns
            )

            # print("end matching")
            #flag = False
            #print("====================================================================================")
            #for expected_pattern in formated_expected_lines:
            #    if not any(re.fullmatch(expected_pattern, actual_line) for actual_line in output_lines):
            #        print(expected_pattern)
            #        flag=True
            #if flag:
            #    print(output_lines)
            #print("=====================================================================================")

            similarity_report = []
            if not exact_match and len(expected_lines) <= 100:
                similarity_report = self.computeSimilarityReport(expected_lines, output_lines)

            return {
                "passed": exact_match,
                "output": output if not exact_match else "",
                "expected": expected,
                "error": error,
                "similarity_report": similarity_report  # Optional for review
            }
