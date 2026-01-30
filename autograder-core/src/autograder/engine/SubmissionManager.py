import zipfile
import os
import itertools
from typing import List
import re
import inspect
import tempfile
import shutil

from autograder.logging.Logger import Logger
from autograder.data.FolderStructure import FolderStructureData, FileType#, FILE_TYPE_EXTENSIONS

class SubmissionManager:
    def __init__(self, config: dict, logger: Logger):
        self.folderStructure = config['folderStructure']
        self.roosterPath = config["roosterPath"]
        self.defaultFilesToCopy = config.get("defaultFilesToCopy", [])
        self.logger = logger
        self.logObjectTemplate = {"Component": "SubmissionManager"}
        with open(self.roosterPath, 'r', encoding='utf-8') as f:
            self.studentNames = [line.strip() for line in f if line.strip()]

    def generateLogObject (self, additionalData: dict) -> dict:
        logObject = dict(self.logObjectTemplate)
        logObject.update(additionalData)
        return logObject

    def extractSubmissions(self, zip_path: str, extract_to: str) -> bool:
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        except Exception as e:
            self.logger.error(
                self.generateLogObject({"Operation": inspect.currentframe().f_code.co_name, "FilePath": zip_path, "ExtractingTo": extract_to, "Error": e})
            )
            return False
        return True
    
    def copyDefaultFiles(self, submission_path: str) -> bool:
        for fileMetaData in self.defaultFilesToCopy:
            new_path = os.path.join(submission_path, os.path.basename(fileMetaData["destinationPath"]))
            shutil.copy2(fileMetaData["sourcePath"], new_path)

    def validateFolderStructure(self, submission_path: str, expected_structure: List['FolderStructureData']) -> dict:

        try:
            report = {
                "missing": [],
                "unexpected": []
            }

            actual_entries = set(os.listdir(submission_path))
            expected_entries = set()

            for item in expected_structure:
                expected_name = item.fileName
                expected_entries.add(expected_name)
                full_path = os.path.join(submission_path, expected_name)

                if item.fileType == FileType.FOLDER:
                    if not os.path.isdir(full_path):
                        report["missing"].append(os.path.basename(full_path) + " (missing folder)")
                    else:
                        subreport = self.validateFolderStructure(full_path, item.Content or [])
                        report["missing"].extend(subreport["missing"])
                        report["unexpected"].extend(subreport["unexpected"])
                else:
                    if not os.path.isfile(full_path):
                        report["missing"].append(os.path.basename(full_path) + " (missing file)")
                    # else:
                    #     expected_ext = FILE_TYPE_EXTENSIONS.get(item.fileType, "")
                    #     if expected_ext and not full_path.lower().endswith(expected_ext):
                    #         report["missing"].append(os.path.basename(full_path) + f" (wrong extension, expected: {expected_ext})")

            # Check for unexpected files/folders
            for entry in actual_entries - expected_entries:
                report["unexpected"].append(entry)
        except Exception as e:
            self.logger.error(
                self.generateLogObject({"Operation": inspect.currentframe().f_code.co_name, "submission_path": submission_path, "expected_structure": expected_structure, "error": e})
            )
            raise e
        
        return report
    
    def checkForLateSubmission(self, submission_path: str) -> bool:
        return "late" in submission_path.lower()


    def validateStructure(self, submission_path: str) -> dict:
        return self.validateFolderStructure(submission_path, self.folderStructure)

    def parseASUIdAndStudentNameFromFilename(self, filename):
        id_match = re.search(r'(\d{10})(?=(?:-\d+)*(\.zip)*$)', filename)

        asu_id = id_match.group(1) if id_match else None
        if not asu_id:
            asu_id = "Not Found in : " + filename

        name_token = re.sub(r'[_\-]?\d{6,}|project|Project|zip|LATE', '', filename, flags=re.IGNORECASE)
        name_token = re.sub(r'[^a-zA-Z]', ' ', name_token).lower().strip()

        matches = []

        for full_name in self.studentNames:
            words = full_name.lower().split()
            permutations = itertools.permutations(words)
            for perm in permutations:
                joined = ''.join(perm)
                if joined in name_token:
                    matches.append(full_name)
                    break

        if len(matches) == 1:
            return {
                "asu_id": asu_id,
                "name": matches[0]
            }
        elif len(matches) == 0:
            raise ValueError(f"No name match found for file: {filename}, extracted {name_token}")
        else:
            raise ValueError(f"Ambiguous match for file: {filename}. Matches: {matches}")
        

    def flattenDirectory(self, submissionPath: str) -> dict:
        flat_files = {}
        for root, _, files in os.walk(submissionPath):
            for file in files:
                flat_files[file.lower()] = os.path.join(root, file)

        return flat_files

    def buildExpectedStructureMap(self, structure: List[FolderStructureData], current_path: str = "") -> dict:
        expected = {}
        for item in structure:
            target_path = os.path.join(current_path, item.fileName)
            if item.fileType == FileType.FOLDER:
                expected.update(self.buildExpectedStructureMap(item.Content, target_path))
            else:
                expected[item.fileName] = (target_path, item.misnomers)
        return expected
    
    def fixFolderStructure (self, sourceFolder: str, destFolder: str):
        flat_files = self.flattenDirectory(sourceFolder)
        expected_map = self.buildExpectedStructureMap(self.folderStructure)

        for expected_name, value in expected_map.items():
            relative_path, misnomers = value
            dest_file_path = os.path.join(destFolder, relative_path)
            os.makedirs(os.path.dirname(dest_file_path), exist_ok=True)

            if expected_name in flat_files:
                shutil.copy2(flat_files[expected_name], dest_file_path)
            else:
                found = False
                for misnomer in misnomers:
                    for file in flat_files.keys():
                        pattern = re.compile(misnomer)
                        if pattern.match(file):
                            #Todo: Keep the original extension
                            shutil.copy2(flat_files[file], dest_file_path)
                            found = True
                            break

                if not found:
                    raise FileNotFoundError("Unable to Fix Folder Structure.. Some File Missing.. => " + expected_name)
            
    def safelyFixFolderStructure (self, sourceFolder):
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                self.fixFolderStructure(
                    sourceFolder,
                    temp_dir
                )

                for item in os.listdir(sourceFolder):
                    item_path = os.path.join(sourceFolder, item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    else:
                        shutil.rmtree(item_path)

                for root, dirs, files in os.walk(temp_dir):
                    rel_path = os.path.relpath(root, temp_dir)
                    target_dir = os.path.join(sourceFolder, rel_path)
                    os.makedirs(target_dir, exist_ok=True)

                    for file in files:
                        shutil.copy2(os.path.join(root, file), os.path.join(target_dir, file))

            except Exception as e:
                print(e)
                raise e



