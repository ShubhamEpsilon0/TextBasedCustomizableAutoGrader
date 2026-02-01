import os
import re
import shutil
import tempfile
from typing import List, Dict
from autograder.data.FolderStructure import FileType, FolderStructureData
from autograder.logging.Logger import Logger
import inspect

class SubmissionStructureFixer:
    """
    Fixes a submission folder to match the expected folder structure.
    Supports misnomers and recursive folder flattening.
    """

    def __init__(self, expected_structure: List[FolderStructureData], defaultFiles: List, testFolderPath: str, logger: Logger):
        self.expected_structure = expected_structure
        self.logger = logger
        self.defaultFilesToCopy = defaultFiles
        self.component = "SubmissionStructureFixer"
        self.testFolderPath = testFolderPath
        self.logger.info({
            "Component": self.component,
            "Status": "SubmissionStructureFixer Initialized"
        })

    def _logTemplate(self, message: dict) -> dict:
        return {
            "Component": self.component,
            "Operation": inspect.currentframe().f_back.f_code.co_name,
            "Message": message
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def safely_fix(self, submission_path: str):
        """
        Safely fix folder structure in a temp directory and copy back.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            self._fix_structure(submission_path, temp_dir)
            self._replace_directory_contents(temp_dir, submission_path)

    def copy_default_files(self, submission_path: str):
        for fileMetaData in self.defaultFilesToCopy:
            new_path = os.path.join(submission_path, os.path.basename(fileMetaData["destinationPath"]))
            shutil.copy2(fileMetaData["sourcePath"], new_path)


    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _flatten_directory(self, root: str) -> Dict[str, str]:
        """
        Returns dict of lowercase filenames -> full path.
        """
        flat_files = {}
        for dirpath, _, files in os.walk(root):
            for f in files:
                flat_files[f.lower()] = os.path.join(dirpath, f)
        return flat_files

    def _build_expected_map(self, structure: List[FolderStructureData], prefix: str = "") -> Dict[str, tuple]:
        """
        Returns dict: expected filename -> (relative path, misnomers)
        """
        result = {}
        for item in structure:
            path = os.path.join(prefix, item.fileName)
            if item.fileType == FileType.FOLDER:
                result.update(self._build_expected_map(item.Content, path))
            else:
                result[item.fileName.lower()] = (path, item.misnomers)
        return result

    def _match_misnomer(self, flat_files: Dict[str, str], patterns: List[str], expected_name: str) -> str | None:
        """
        Returns first matching file from flat_files for given misnomer patterns.
        """
        for pattern in patterns:
            regex = re.compile(pattern)
            for fname in flat_files:
                if regex.match(fname):
                    self.logger.info(self._logTemplate({
                        "Looking for": expected_name,
                        "Misnomer matched with": fname,
                        "Against pattern": pattern
                    }))
                    return fname
        return None

    def _fix_structure(self, source: str, target: str):
        """
        Copy files from source to target according to expected structure.
        """
        flat_files = self._flatten_directory(source)
        expected_map = self._build_expected_map(self.expected_structure)

        for expected_name, (relative_path, misnomers) in expected_map.items():
            dest_file_path = os.path.join(target, relative_path)
            os.makedirs(os.path.dirname(dest_file_path), exist_ok=True)

            if expected_name in flat_files:
                shutil.copy2(flat_files[expected_name], dest_file_path)
                continue

            matched_file = self._match_misnomer(flat_files, misnomers, expected_name)
            if matched_file:
                shutil.copy2(flat_files[matched_file], dest_file_path)
                continue

            self.logger.error(self._logTemplate({
                "Error": f"Missing required file: {expected_name}, files available: {list(flat_files.keys())}"
            }))
            raise FileNotFoundError(f"Missing required file: {expected_name}")

    def _replace_directory_contents(self, source: str, target: str):
        """
        Replace the contents of target folder with source folder safely.
        """
        try:
            # Remove old contents
            for entry in os.listdir(target):
                path = os.path.join(target, entry)
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)

            # Copy new contents
            for root, _, files in os.walk(source):
                rel_path = os.path.relpath(root, source)
                dest_dir = os.path.join(target, rel_path)
                os.makedirs(dest_dir, exist_ok=True)
                for f in files:
                    shutil.copy2(os.path.join(root, f), os.path.join(dest_dir, f))
        except Exception as e:
            self.logger.error(self._logTemplate({
                "Source": source,
                "Target": target,
                "Error": str(e)
            }))
            raise

