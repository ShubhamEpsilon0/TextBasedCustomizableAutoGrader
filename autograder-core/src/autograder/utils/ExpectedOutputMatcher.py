import re
from typing import Dict, List, Tuple, Optional
import difflib

PLACEHOLDER_PATTERN = re.compile(r"<([A-Z0-9_]+)>")

class ExpectedOutputMatcher:
    def __init__(self, placeholderRegex: Dict[str, str]):
        """
        placeholderRegex example:
        {
            "INT": "[0-9]+",
            "ADDR": "(0x)?[0-9a-fA-F]{8,16}"
        }
        """
        self.placeholderRegex = placeholderRegex

    def compileExpectedLines(self, expectedLines: List[str]) -> List[re.Pattern]:
        compiled = []

        for line in expectedLines:
            regex_line = re.escape(line)

            for placeholder, pattern in self.placeholderRegex.items():
                escaped = re.escape(f"<{placeholder}>")
                regex_line = regex_line.replace(escaped, f"({pattern})")
                line = line.replace(f"<{placeholder}>", "")

            regex_line = regex_line.replace(r"\ ", r"\s+")
            # allow extra text before/after
            # regex_line = "^" + regex_line + "$"
            compiled.append((line, re.compile(regex_line, re.IGNORECASE)))

        return compiled

    # def match(self, expectedLines: List[str], actualLines: List[str]) -> bool:
    #     compiledPatterns = self.compileExpectedLines(expectedLines)
    #     actualSet = set(actualLines)
    #     return all(
    #         any(pattern.search(line) for line in actualSet)
    #         for pattern in compiledPatterns
    #     )

    def match(self, expectedLines: List[str], actualLines: List[str]) -> bool:
        compiledPatterns = self.compileExpectedLines(expectedLines)
        dissimilarity_report = []
        all_matched = True
        generate_similarity_report = len(expectedLines) <= 200

        for expected_text, pattern in compiledPatterns:
            best_line = None
            best_score = 0.0

            for line in actualLines:
                if pattern.search(line):
                    best_line = line
                    best_score = 1.0
                    break
                else:
                    if generate_similarity_report:
                        score = self._similarity(expected_text, line)
                        if score > best_score:
                            best_score = score
                            best_line = line

            if best_score < 1.0:
                all_matched = False
                dissimilarity_report.append({
                    "expected_line": expected_text,
                    "closest_match": best_line,
                    "similarity_score": best_score
                })

        return all_matched, dissimilarity_report
    
    def _similarity(self, a: str, b: str) -> float:
        return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()
