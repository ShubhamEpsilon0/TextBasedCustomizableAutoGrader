import re
from typing import Dict, List

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

            # allow extra text before/after
            regex_line = "^" + regex_line + "$"
            compiled.append(re.compile(regex_line))

        return compiled

    def match(self, expectedLines: List[str], actualLines: List[str]) -> bool:
        compiledPatterns = self.compileExpectedLines(expectedLines)
        actualSet = set(actualLines)

        return all(
            any(pattern.fullmatch(line) for line in actualSet)
            for pattern in compiledPatterns
        )
