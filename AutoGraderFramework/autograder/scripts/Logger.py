import json
from enum import Enum
import time

class LogLevel(Enum):
    INFO = 1
    WARNING = 2
    ERROR = 3

class Logger:

    def __init__(self, logFileName):
        self.logFileName = logFileName
        self.logHandle = open(self.logFileName, "w")
        self.logLevel = LogLevel.ERROR

    def setLogLevel(self, level):
        self.logLevel = level

    def info(self, logObject):
        if self.logLevel.value <= LogLevel.INFO.value:
            self.log(logObject, LogLevel.INFO)
    
    def warning(self, logObject):
        if self.logLevel.value <= LogLevel.WARNING.value:
            self.log(logObject, LogLevel.WARNING)
    
    def error(self, logObject):
        self.log(logObject, LogLevel.ERROR)

    def log (self, logObject, level=LogLevel.INFO):
        self.logHandle.write(json.dumps({
            "timestamp": time.time(),
            "level": level.name,
            "message": logObject
        }) + "\n")