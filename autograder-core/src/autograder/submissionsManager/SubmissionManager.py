from .Extractor import Extractor
from .SubmissionStructureValidator import SubmissionStructureValidator
from .SubmissionStructureFixer import SubmissionStructureFixer
from .FilenameParser import FilenameParser
from autograder.logging.Logger import Logger

class SubmissionManager:
    def __init__(self, config: dict, logger: Logger):
        self.logger = logger
        self.extractor = Extractor(logger)
        self.validator = SubmissionStructureValidator(config.get("folderStructure", []), logger)
        self.fixer = SubmissionStructureFixer(config.get("folderStructure", []), config.get("defaultFilesToCopy", []), config.get("testFolderPath", ""), logger)
        self.resolver = FilenameParser(config.get("roosterPath"), logger)

    # Public API
    def extractSubmissions(self, zip_path: str, extract_to: str) -> bool:
        return self.extractor.extract(zip_path, extract_to)

    def validateStructure(self, path: str) -> dict:
        return self.validator.validate(path)

    def safelyFixFolderStructure(self, path: str):
        self.fixer.safely_fix(path)

    def copyDefaultFiles(self, path: str):
        self.fixer.copy_default_files(path)

    def parseASUIdAndStudentNameFromFilename(self, filename: str) -> dict:
        return self.resolver.parse(filename)

    def checkForLateSubmission(self, filename: str) -> bool:
        return "late" in filename.lower()
