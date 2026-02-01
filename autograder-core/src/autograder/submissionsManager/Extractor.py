import zipfile
import inspect
from autograder.logging.Logger import Logger

class Extractor:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.component = "File Extractor"

    def extract(self, zip_path: str, extract_to: str) -> bool:
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            return True
        except Exception as e:
            self.logger.error({
                "Component": self.component,
                "Operation": inspect.currentframe().f_code.co_name,
                "ZipPath": zip_path,
                "Target": extract_to,
                "Error": str(e)
            })
            return False
