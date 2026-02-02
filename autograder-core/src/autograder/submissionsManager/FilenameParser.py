import itertools
import re
from typing import List
import inspect

from autograder.logging.Logger import Logger

class FilenameParser:
    def __init__(self, roster_path: str, logger: Logger):
        self.studentNames = self._load_roster(roster_path)
        self.logger = logger
        self.component = "FilenameParser"
        self.parsedCount = 0
        self.logger.info(
            self._logTemplate({
                "RosterPath": roster_path,
                "TotalStudentsLoaded": len(self.studentNames),
                "Status": "FilenameParser Initialized"
            })
        )

    def _logTemplate(self, message: dict) -> dict:
        return {
            "Component": self.component,
            "Operation": inspect.currentframe().f_back.f_code.co_name,
            "Message": message
        }
        
    def _load_roster(self, path: str) -> List[str]:
        if not path:
            self.logger.error(
                self._logTemplate({
                    "Error": "Roster path is required but not provided."
                })
            )
            raise ValueError("Roster path is required")
        with open(path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]

    def parse(self, filename: str) -> dict:
        asu_id = self._extract_asu_id(filename)
        name = self._match_name(filename)
        self.parsedCount += 1
        return {"asu_id": asu_id, "name": name or "Unknown"}

    def _extract_asu_id(self, filename: str) -> str:
        match = re.search(r'(\d{10})(?=(?:-\d+)*(\.zip)*$)', filename)
        return match.group(1) if match else f"Not Found in: {filename}"

    def _match_name(self, filename: str) -> str | None:
        token = re.sub(r'[_\-]?\d{6,}|project|zip|late', '', filename, flags=re.IGNORECASE)
        token = re.sub(r'[^a-zA-Z]', ' ', token).lower()

        matches = []
        for full_name in self.studentNames:
            words = full_name.lower().split()
            for perm in itertools.permutations(words):
                if ''.join(perm) in token:
                    matches.append(full_name)
                    break
        if len(matches) == 1:
            return matches[0]
        elif len(matches) == 0:
            self.logger.error(
                self._logTemplate({
                    "Error": f"No name match found for file: {filename}, extracted {token}"
                })
            )
            raise ValueError(f"No name match found for file: {filename}, extracted {token}")
        else:
            self.logger.error(
                self._logTemplate({
                    "Error": f"Ambiguous match for file: {filename}. Matches: {matches}"
                })
            )
            raise ValueError(f"Ambiguous match for file: {filename}. Matches: {matches}")
        
    def finalize(self):
        self.logger.info(
            self._logTemplate({
                "TotalParsedFiles": self.parsedCount
            })
        )

