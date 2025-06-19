import os
import sys
import tempfile
from dataclasses import dataclass, field
import json
import shutil

from autograder.scripts.data.DictMixin import DictMixin
from autograder.scripts.ShellScriptTestRunner import ShellScriptTestRunner
from autograder.scripts.ExcelResultWriter import ExcelResultWriter
from autograder.scripts.data.ResultData import ResultObject, TestResult
from autograder.scripts.monitoring.LiveMonitor import Monitor
from autograder.scripts.monitoring.DictTableBuilder import DictTableBuilder
from autograder.scripts.ProgressLogger import ProgressLogger
from autograder.scripts.SubmissionManager import SubmissionManager

# sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test'))
# print(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test'))


# from test.config import testConfig


from autograder.scripts.SubmissionManager import FolderStructureData, FileType
fatalErros = [
    "❌ Make Install Failed",
    "codec can't decode byte"
]

testConfig = {
    "MakeFilePath": "../test/copyableFiles/Makefile",
    "CommonFilePath": "../test/copyableFiles/ioctl-defines.h",
    "fatalErrors": fatalErros,
    "roosterPath": "../studentNames.txt",
    "loggingOn": False,
    "folderStructure": [
        FolderStructureData("kmodule", FileType.FOLDER, [
            FolderStructureData("Makefile", FileType.MAKEFILE),
            FolderStructureData("kmod-ioctl.c", FileType.C),
            FolderStructureData("kmod-main.c", FileType.C),
        ]),
        FolderStructureData("ioctl-defines.h", FileType.H),
    ],
    "submissionsPath": "../../submissions/",
    "testConfig": {
        "runScriptPath": "../test/test.sh",
        "buildScriptPath": "",
        "testCases": [  
            {
                "TestName": "TestRead",
                "inputLine": "read",
                "expectedOutputFilePath": "../test/testcases/TestReadOutput.txt",
                "maxTestScore": 15
            },
            {
                "TestName": "TestWrite",
                "inputLine": "write",
                "expectedOutputFilePath": "../test/testcases/TestWriteOutput.txt",
                "maxTestScore": 15
            },
            {
                "TestName": "TestReadVar512-1-0",
                "inputLine": "read-variable 512 1 0",
                "expectedOutputFilePath": "../test/testcases/TestReadVar512-1-0Output.txt",
                "maxTestScore": 5
            },
            {
                "TestName": "TestWriteVar512-1-0",
                "inputLine": "write-variable 512 1 0",
                "expectedOutputFilePath": "../test/testcases/TestWriteVar512-1-0Output.txt",
                "maxTestScore": 5
            },
            {
                "TestName": "TestReadVar512-1024-0",
                "inputLine": "read-variable 512 1024 0",
                "expectedOutputFilePath": "../test/testcases/TestReadVar512-1024-0Output.txt",
                "maxTestScore": 5 + 5 # TestReadVar16384-10000-0
            },
            {
                "TestName": "TestReadVar8192-100-134217728",
                "inputLine": "read-variable 8192 100 134217728",
                "expectedOutputFilePath": "../test/testcases/TestReadVar8192-100-134217728Output.txt",
                "maxTestScore": 5 + 5 # TestReadVar2048-100000-0
            },
            {
                "TestName": "TestWriteVar8192-512-402653184",
                "inputLine": "write-variable 8192 512 402653184",
                "expectedOutputFilePath": "../test/testcases/TestWriteVar8192-512-402653184Output.txt",
                "maxTestScore": 5 + 5 # for TestWriteVar393216-1024-402653184
            },
            {
                "TestName": "TestWriteVar131072-768-0",
                "inputLine": "write-variable 131072 768 0",
                "expectedOutputFilePath": "../test/testcases/TestWriteVar131072-768-0Output.txt",
                "maxTestScore": 5
            },
            #{
            #    "TestName": "TestWriteVar393216-1024-402653184",
            #    "inputLine": "write-variable 393216 1024 402653184",
            #    "expectedOutputFilePath": "../test/testcases/TestWriteVar393216-1024-402653184Output.txt",
            #    "maxTestScore": 5
            #},
            {
                "TestName": "TestWriteVar512-100000-0",
                "inputLine": "write-variable 512 100000 0",
                "expectedOutputFilePath": "../test/testcases/TestWriteVar512-100000-0Output.txt",
                "maxTestScore": 5
            },
            #{
            #    "TestName": "TestReadVar2048-100000-0",
            #    "inputLine": "read-variable 2048 100000 0",
            #    "expectedOutputFilePath": "../test/testcases/TestReadVar2048-100000-0Output.txt",
            #    "maxTestScore": 5
            #},
            {
                "TestName": "TestReadVar512-10000-131072",
                "inputLine": "read-variable 512 10000 131072",
                "expectedOutputFilePath": "../test/testcases/TestReadVar512-100000-131072Output.txt",
                "maxTestScore": 5 + 5 # for TestReadVar16384-10000-1048576
            },
            {
                "TestName": "TestWriteVar2048-10000-16384",
                "inputLine": "write-variable 2048 10000 16384",
                "expectedOutputFilePath": "../test/testcases/TestWriteVar2048-100000-16384Output.txt",
                "maxTestScore": 5
            },
            {
                "TestName": "TestWriteVar8192-10000-0",
                "inputLine": "write-variable 8192 10000 0",
                "expectedOutputFilePath": "../test/testcases/TestWriteVar8192-100000-0Output.txt",
                "maxTestScore": 5
            },
            #{
            #    "TestName": "TestReadVar16384-10000-0",
            #    "inputLine": "read-variable 16384 10000 0",
            #    "expectedOutputFilePath": "../test/testcases/TestReadVar16384-100000-0Output.txt",
            #    "maxTestScore": 5
            #},
            #{
            #    "TestName": "TestReadVar16384-10000-1048576",
            #     "inputLine": "read-variable 16384 10000 1048576",
            #    "expectedOutputFilePath": "../test/testcases/TestReadVar16384-100000-1048576Output.txt",
            #    "maxTestScore": 5
            #},
        ]
    },
    "resultsFilePath": "../results.xlsx"
}



@dataclass
class GradingSummary(DictMixin):
    TotalSubmissions: int = field(metadata={"alias":"Total Submissions to be Graded"}, default=0)
    SubmissionsGraded: int = field(metadata={"alias":"Submissions Graded"}, default=0)
    TestCasesPassed: int = field(metadata={"alias":"✅ Total Test Cases Passed"}, default=0)
    TestCasesFailed: int = field(metadata={"alias":"❌ Total Test Cases Failed"}, default=0)
    SkippedSubmissions: int = field(metadata={"alias":"⚠️ Skipped Submissions"}, default=0)
    FullMarksSubmissionCount: int =  field(metadata={"alias":"Submissions Full Marks Count"}, default=0)

@dataclass
class CurrentOperationState(DictMixin):
    CurrentStudentFile: str = field(metadata={"alias":"Current Student File"}, default="")
    CurrentOperation: str = field(metadata={"alias":"Current Operation"}, default="")

# tempFolderPath = "/mnt/tmp" if os.path.exists("/mnt/tmp") else os.environ["TMPDIR"]

class AutoGraderP5:
    
    GRADING_SUMMARY_TABLENAME = "Grading Summary"
    CURRENT_OPERATION_TABLENAME = "Current Operation State"
    GRADED_SUBMISSIONS="Graded Submissions"

    def __init__(self, testConfig):
        # os.environ["TMPDIR"] = tempFolderPath
        self.config = testConfig
        self.resumeLogArea = "./autograder/logs/gradedLogs"

        self.testRunner = ShellScriptTestRunner (self.config["testConfig"]["buildScriptPath"], self.config["testConfig"]["runScriptPath"], self.config["fatalErrors"])
        self.writer = ExcelResultWriter(self.config["resultsFilePath"])
        self.writer.InitializeWriter()
                        
        self.gradingSummary = GradingSummary()
        self.currentGradingState = CurrentOperationState()
        self.gradedSubmissions = set()

        self.monitor = Monitor()
        summaryTable = DictTableBuilder(AutoGraderP5.GRADING_SUMMARY_TABLENAME, ["Metric", "Value"])
        currentOpsTable = DictTableBuilder(AutoGraderP5.CURRENT_OPERATION_TABLENAME, ["Key", "Value"])

        self.monitor.addTable(AutoGraderP5.GRADING_SUMMARY_TABLENAME, summaryTable)
        self.monitor.addTable(AutoGraderP5.CURRENT_OPERATION_TABLENAME, currentOpsTable)

        self.progressLogger = ProgressLogger(self.resumeLogArea)
        loadedProgress = self.progressLogger.loadProgressLog()
        if loadedProgress:
            self.gradingSummary = GradingSummary.fromDict(loadedProgress[-1][AutoGraderP5.GRADING_SUMMARY_TABLENAME])
            self.currentGradingState = CurrentOperationState.fromDict(loadedProgress[-1][AutoGraderP5.CURRENT_OPERATION_TABLENAME])
            self.gradedSubmissions = set(loadedProgress[-1][AutoGraderP5.GRADED_SUBMISSIONS])

            print(self.gradingSummary)
            print(self.currentGradingState)

        self.progressLogger.InitializeForLogging()
        self.monitor.start()
        self.submissionManager = SubmissionManager(self.config)

    def updateMonitoringData(self, tablesToUpdate): 
        if AutoGraderP5.GRADING_SUMMARY_TABLENAME in tablesToUpdate:
            self.monitor.updateTable(AutoGraderP5.GRADING_SUMMARY_TABLENAME, self.gradingSummary)
        if AutoGraderP5.CURRENT_OPERATION_TABLENAME in tablesToUpdate:
            self.monitor.updateTable(AutoGraderP5.CURRENT_OPERATION_TABLENAME, self.currentGradingState)

        self.monitor.refresh()

    def grade(self):
        student_eval_result = None
        try:
            unzipped_submissions_path = self.config["submissionsPath"]
            self.gradingSummary.TotalSubmissions = len(os.listdir(unzipped_submissions_path))
            student_submissions = os.listdir(unzipped_submissions_path)
            student_submissions.sort()

            for student_file in student_submissions:
                if student_file in self.gradedSubmissions:
                    continue

                self.currentGradingState.CurrentStudentFile = student_file
                self.currentGradingState.CurrentOperation = "Extracting Submission"
                
                self.updateMonitoringData([AutoGraderP5.CURRENT_OPERATION_TABLENAME, AutoGraderP5.GRADING_SUMMARY_TABLENAME])
                
                with tempfile.TemporaryDirectory() as individual_submission_temp_dir:
                    student_zip_path = os.path.join(unzipped_submissions_path, student_file)
                    student_eval_result = ResultObject()

                    if not self.submissionManager.extractSubmissions(student_zip_path, individual_submission_temp_dir):
                        self.gradingSummary.SkippedSubmissions += 1
                        student_eval_result.SubmissionError = "Unable to extract from Student Submission folder.."
                        self.writer.writeTestResult(student_eval_result)
                        self.gradedSubmissions.add(student_file)
                        self.gradingSummary.SubmissionsGraded += 1
                        
                        self.progressLogger.logProgress({
                            AutoGraderP5.GRADING_SUMMARY_TABLENAME: dict(self.gradingSummary),
                            AutoGraderP5.CURRENT_OPERATION_TABLENAME: dict(self.currentGradingState),
                            AutoGraderP5.GRADED_SUBMISSIONS: list(self.gradedSubmissions)
                        })

                        self.updateMonitoringData([AutoGraderP5.GRADING_SUMMARY_TABLENAME])
                        continue

                    student_path = os.path.join(individual_submission_temp_dir, "")

                    self.currentGradingState.CurrentOperation = "Parsing ASU Id and FileName"
                    student_info = self.submissionManager.parseASUIdAndStudentNameFromFilename(student_file)
                    student_id, student_name = student_info["asu_id"], student_info["name"]

                    student_eval_result.StudentName = student_name
                    student_eval_result.AsuId = student_id

                    self.updateMonitoringData([AutoGraderP5.CURRENT_OPERATION_TABLENAME])


                    if self.submissionManager.checkForLateSubmission(student_file):
                        self.gradingSummary.SkippedSubmissions += 1
                        student_eval_result.SubmissionError = "Late Submission...."
                        self.writer.writeTestResult(student_eval_result)
                        self.gradedSubmissions.add(student_file)
                        self.gradingSummary.SubmissionsGraded += 1
                        self.progressLogger.logProgress({
                            AutoGraderP5.GRADING_SUMMARY_TABLENAME: dict(self.gradingSummary),
                            AutoGraderP5.CURRENT_OPERATION_TABLENAME: dict(self.currentGradingState),
                            AutoGraderP5.GRADED_SUBMISSIONS: list(self.gradedSubmissions)
                        })

                        self.updateMonitoringData([AutoGraderP5.CURRENT_OPERATION_TABLENAME, AutoGraderP5.GRADING_SUMMARY_TABLENAME])
                        continue

                    self.currentGradingState.CurrentOperation = "Validating Folder Structure"
                    structure_report = self.submissionManager.validateStructure(student_path)

                    shutil.copy2(self.config["MakeFilePath"], individual_submission_temp_dir)
                    shutil.copy2(self.config["CommonFilePath"], individual_submission_temp_dir)

                    self.updateMonitoringData([AutoGraderP5.CURRENT_OPERATION_TABLENAME])
                    student_eval_result.StructureErrors = structure_report
                    if len(structure_report["missing"]) > 0:
                        try:
                            self.currentGradingState.CurrentOperation = "Attempting to fix folder strucuture"
                            self.updateMonitoringData([AutoGraderP5.CURRENT_OPERATION_TABLENAME])
                            self.submissionManager.safelyFixFolderStructure(individual_submission_temp_dir)
                        except:
                            self.gradingSummary.SkippedSubmissions += 1
                            self.writer.writeTestResult(student_eval_result)
                            self.gradedSubmissions.add(student_file)
                            self.gradingSummary.SubmissionsGraded += 1
                            self.progressLogger.logProgress({
                                AutoGraderP5.GRADING_SUMMARY_TABLENAME: dict(self.gradingSummary),
                                AutoGraderP5.CURRENT_OPERATION_TABLENAME: dict(self.currentGradingState),
                                AutoGraderP5.GRADED_SUBMISSIONS: list(self.gradedSubmissions)
                            })
                            self.updateMonitoringData([AutoGraderP5.GRADING_SUMMARY_TABLENAME])
                            continue

                    makeFileStudentPath = os.path.join(individual_submission_temp_dir, "kmodule")

                    shutil.copy2(self.config["MakeFilePath"], makeFileStudentPath)
                    shutil.copy2(self.config["CommonFilePath"], individual_submission_temp_dir)
                    # self.currentGradingState.CurrentOperation = "Building Submission"
                    # buildSuccess, output, error = self.testRunner.build(individual_submission_temp_dir)
                    # self.updateMonitoringData([AutoGraderP5.CURRENT_OPERATION_TABLENAME])
                    # if not buildSuccess:
                    #     student_eval_result.SubmissionError = "Failed to Compile\n\n\n" + (output if output else "") +"\n\n\n" + (error if error else "")
                    #     self.gradingSummary.SkippedSubmissions += 1
                    #     self.writer.writeTestResult(student_eval_result)
                    #     self.gradedSubmissions.add(student_file)
                    #     self.gradingSummary.SubmissionsGraded += 1
                    #     self.progressLogger.logProgress({
                    #         AutoGraderP5.GRADING_SUMMARY_TABLENAME: dict(self.gradingSummary),
                    #         AutoGraderP5.CURRENT_OPERATION_TABLENAME: dict(self.currentGradingState),
                    #         AutoGraderP5.GRADED_SUBMISSIONS: list(self.gradedSubmissions)
                    #     })
                    #     self.updateMonitoringData([AutoGraderP5.GRADING_SUMMARY_TABLENAME])
                    #     continue

                    for testcase in self.config["testConfig"]["testCases"]:
                        self.currentGradingState.CurrentOperation = "Running TestCase: " + testcase["TestName"]
                        self.updateMonitoringData([AutoGraderP5.CURRENT_OPERATION_TABLENAME])
                        inputLine = testcase["inputLine"]
                        expectedOutputFilePath = testcase["expectedOutputFilePath"]

                        res = self.testRunner.run(inputLine, expectedOutputFilePath, individual_submission_temp_dir)
                        # print("Report Genereated")
                        if res["passed"] == True:
                            self.gradingSummary.TestCasesPassed += 1
                            student_eval_result.FinalScore += testcase["maxTestScore"]
                        else:
                            # print(res)
                            self.gradingSummary.TestCasesFailed += 1

                        test_result = TestResult(testcase["TestName"], res["passed"], res["output"], json.dumps(res["similarity_report"]), res["error"])
                        student_eval_result.TestResults.append(test_result)
                        self.updateMonitoringData([AutoGraderP5.GRADING_SUMMARY_TABLENAME])

                    self.writer.writeTestResult(student_eval_result)
                    self.gradingSummary.FullMarksSubmissionCount += 1 if all(testRes.Passed for testRes in student_eval_result.TestResults) else 0

                    self.gradedSubmissions.add(student_file)
                    self.gradingSummary.SubmissionsGraded += 1
                    self.progressLogger.logProgress({
                        AutoGraderP5.GRADING_SUMMARY_TABLENAME: dict(self.gradingSummary),
                        AutoGraderP5.CURRENT_OPERATION_TABLENAME: dict(self.currentGradingState),
                        AutoGraderP5.GRADED_SUBMISSIONS: list(self.gradedSubmissions)
                    })
                    self.updateMonitoringData([AutoGraderP5.CURRENT_OPERATION_TABLENAME, AutoGraderP5.GRADING_SUMMARY_TABLENAME])

            self.updateMonitoringData([AutoGraderP5.CURRENT_OPERATION_TABLENAME, AutoGraderP5.GRADING_SUMMARY_TABLENAME])
        except Exception as e:
            self.monitor.stop()
            print(f"Error during grading: {e}")
        except SystemExit as se:
            self.monitor.stop()
            print(str(se))
            if "Autograder terminated due to fatal error" in str(se):
                self.gradedSubmissions.add(self.currentGradingState.CurrentStudentFile)
                self.gradingSummary.SubmissionsGraded += 1
                self.progressLogger.logProgress({
                    AutoGraderP5.GRADING_SUMMARY_TABLENAME: dict(self.gradingSummary),
                    AutoGraderP5.CURRENT_OPERATION_TABLENAME: dict(self.currentGradingState),
                    AutoGraderP5.GRADED_SUBMISSIONS: list(self.gradedSubmissions)
                })
                self.updateMonitoringData([AutoGraderP5.CURRENT_OPERATION_TABLENAME, AutoGraderP5.GRADING_SUMMARY_TABLENAME])
                student_eval_result.SubmissionError = "Fatal Error Occured..."
                self.writer.writeTestResult(student_eval_result)


if __name__ == "__main__":
    AutoGraderP5(testConfig).grade()


                    

        

    
