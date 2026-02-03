import os
import inspect
from typing import List
from autograder.data.FolderStructure import FolderStructureData, FileType
from autograder.logging.Logger import Logger

class SubmissionStructureValidator:
    """
    Validates that a submission matches the expected folder structure.
    Returns a report dict with "missing" and "unexpected" entries.
    """

    def __init__(self, expected_structure: List[FolderStructureData], logger: Logger):
        self.expected_structure = expected_structure
        self.logger = logger
        self.component = "SubmissionStructureValidator"
        self.logger.info(
            self._log_template({
                "Status": "SubmissionStructureValidator Initialized"
            })
        )
        self.validFolders = 0
        self.totalValidations = 0

    def _log_template(self, message: dict) -> dict:
        return {
            "Component": self.component,
            "Operation": inspect.currentframe().f_back.f_code.co_name,
            "Message": message
        }

    def validate(self, submission_path: str) -> dict:
        """
        Recursively validate folder structure.
        Returns {"missing": [...], "unexpected": [...]}
        """
        self.totalValidations += 1
        return self._validate_folder(submission_path, self.expected_structure)

    def _validate_folder(self, base_path: str, expected: List[FolderStructureData]) -> dict:
        report = {"missing": [], "unexpected": []}

        try:
            actual_entries = set(os.listdir(base_path))
            expected_entries = {item.fileName for item in expected}

            # Check each expected item
            for item in expected:
                full_path = os.path.join(base_path, item.fileName)

                if item.fileType == FileType.FOLDER:
                    if not os.path.isdir(full_path):
                        report["missing"].append(f"{item.fileName} (missing folder)")
                    else:
                        sub_report = self._validate_folder(full_path, item.Content or [])
                        report["missing"].extend(sub_report["missing"])
                        report["unexpected"].extend(sub_report["unexpected"])
                else:
                    if not os.path.isfile(full_path):
                        report["missing"].append(f"{item.fileName} (missing file)")

            # Detect unexpected files/folders
            for extra in actual_entries - expected_entries:
                report["unexpected"].append(extra)

        except Exception as e:
            self.logger.error(self._log_template({"submission_path": base_path, "expected_structure": expected, "error": e}))
            raise

        self.validFolders += 1 if len(report["missing"]) == 0 and len(report["unexpected"]) == 0 else 0
        return report
    
    def finalize(self):
        self.logger.info(
            self._log_template({
                "TotalValidations": self.totalValidations,
                "ValidFolders": self.validFolders,
                "Status": "SubmissionStructureValidator Finalized"
            })
        )
