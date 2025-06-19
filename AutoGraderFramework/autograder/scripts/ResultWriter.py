from autograder.scripts.data.ResultData import ResultObject


class ResultWriter:
    def __init__(self, filePath):
        self.filePath = filePath

    def InitializeWriter ():
        raise NotImplementedError
    
    def writeTestResult (result: ResultObject):
        raise NotImplementedError
    
    def FinalizeWriter ():
        raise NotImplementedError
    
