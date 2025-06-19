import json
class Logger:

    def __init__(self, logFileName):
        self.logFileName = logFileName
        self.logHandle = open(self.logFileName, "w")

    def log (self, logObject):
        self.logHandle.write(json.dumps(logObject))