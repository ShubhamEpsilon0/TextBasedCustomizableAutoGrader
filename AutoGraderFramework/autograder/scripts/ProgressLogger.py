import json
import os

class ProgressLogger:
    def __init__(self, logPath: str):
        self.logPath = logPath
        #check if backup file exists
        if os.path.exists(self.logPath + ".bak"):
            try:
                c = str(input("BackUp File Found. Do you want to Load BackUp (Y/N)?"))
                if c[0] == "y" or c == "Y":
                    self.CopyFileContentBetweenFiles(self.logPath + ".bak", self.logPath)
            except Exception as e:
                print(f"Error opening backup file: {e}")
                self.backupFile = None
        self.backupFile = None

    def InitializeForLogging (self):
        if os.path.exists(self.logPath):
            self.CopyFileContentBetweenFiles(self.logPath, self.logPath + ".bak")
        self.logFile = open(self.logPath, 'w')
        pass

    def CopyFileContentBetweenFiles(self, sourcePath: str, destPath: str):
        try:
            with open(sourcePath, 'r') as sourceFile:
                content = sourceFile.read()
            with open(destPath, 'w') as destFile:
                destFile.write(content)
        except Exception as e:
            print(f"Error copying file content: {e}")

    def logProgress(self, data:object, truncatePrevious: bool = True):
        try:
            if truncatePrevious:
                # Backup the current log file before truncating
                self.CopyFileContentBetweenFiles(self.logPath, self.logPath + ".bak")

                self.logFile.seek(0)                # Go to beginning
                self.logFile.truncate()
            
            if isinstance(data, dict):
                self.logFile.write(json.dumps(data) + "\n")
            elif isinstance(data, str):
                self.logFile.write(data + "\n")
            else:
                raise ValueError("Unsupported data type. Must be dict or str.")

            if os.path.exists(self.logPath + ".bak"):
                os.remove(self.logPath + ".bak")
        except Exception as e:
            print(f"Error logging progress: {e}")
        finally:
            if self.logFile:
                self.logFile.flush()

    def loadProgressLog(self) -> list:
        try:
            if not os.path.exists(self.logPath):
                return []  # Return empty list if log file does not exist
            
            with open(self.logPath, 'r') as logFile:
                lines = logFile.readlines()
                try:
                # Parse JSON lines into a list
                    return [json.loads(line.strip()) for line in lines if line.strip()]
                except json.JSONDecodeError as e:
                    return lines
        except Exception as e:
            print(f"Error loading progress log: {e}")
            return []

    
