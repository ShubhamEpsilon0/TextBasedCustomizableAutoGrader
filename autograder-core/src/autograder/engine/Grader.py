import os
import tempfile

from autograder.engine.SubmissionManager import SubmissionManager
from autograder.data.CurrentOperationState import CurrentOperationState
from autograder.script_runner.ShellScriptTestRunner import ShellScriptTestRunner
from autograder.result_writer.ExcelResultWriter import ExcelResultWriter

from autograder.data.GradingContext import GradingContext
from autograder.data.GradingSummary import GradingSummary

from autograder.monitoring.LiveMonitor import Monitor
from autograder.monitoring.DictTableBuilder import DictTableBuilder
from autograder.logging.ProgressLogger import ProgressLogger
from autograder.logging.Logger import Logger

from autograder.steps.ExtractSubmissionStep import ExtractSubmissionStep
from autograder.steps.ParseStudentInfoStep import ParseStudentInfoStep
from autograder.steps.LateSubmissionStep import LateSubmissionStep
from autograder.steps.StructureValidationStep import StructureValidationStep
from autograder.steps.CopyDefaultFilesStep import CopyDefaultFilesStep
from autograder.steps.BuildStep import BuildStep
from autograder.steps.RunTestsStep import RunTestsStep
from autograder.steps.CleanupStep import CleanupStep

class AutoGrader:
    GRADING_SUMMARY_TABLENAME = "Grading Summary"
    CURRENT_OPERATION_TABLENAME = "Current Operation State"
    GRADED_SUBMISSIONS = "Graded Submissions"
    BLACKLISTED_SUBMISSIONS = "Blacklisted Submissions"

    def __init__(self, config):
        self.blacklistedSubmissions = set()
        self.config = config
        self.resumeLogArea = "./logs/gradedLogs.json"
        self.logger = Logger("./logs/operationalLogs.log")

        self.testRunner = ShellScriptTestRunner(
            config["testConfig"]["buildScriptPath"],
            config["testConfig"]["runScriptPath"],
            config["fatalErrors"]
        )

        self.writer = ExcelResultWriter(config["resultsFilePath"])
        self.writer.InitializeWriter()

        self.gradingSummary = GradingSummary()
        self.currentGradingState = CurrentOperationState()
        self.gradedSubmissions = set()

        self.monitor = Monitor()
        self.monitor.addTable(
            self.GRADING_SUMMARY_TABLENAME,
            DictTableBuilder(self.GRADING_SUMMARY_TABLENAME, ["Metric", "Value"])
        )
        self.monitor.addTable(
            self.CURRENT_OPERATION_TABLENAME,
            DictTableBuilder(self.CURRENT_OPERATION_TABLENAME, ["Key", "Value"])
        )

        self.progressLogger = ProgressLogger(self.resumeLogArea)
        self.progressLogger.InitializeForLogging()
        self._load_progress()

        # self.monitor.start()
        self.submissionManager = SubmissionManager(config, self.logger)

        self.pipeline = [
            ExtractSubmissionStep(),
            ParseStudentInfoStep(),
            LateSubmissionStep(),
            StructureValidationStep(),
            CopyDefaultFilesStep(),
            # BuildStep(),
            # RunTestsStep(),
            # CleanupStep("after_submission")
        ]

    # ----------------------------
    # Progress & monitoring helpers
    # ----------------------------

    def _load_progress(self):
        logs = self.progressLogger.loadProgressLog()
        if not logs:
            return

        last = logs[-1]
        self.gradingSummary = GradingSummary.fromDict(
            last[self.GRADING_SUMMARY_TABLENAME]
        )
        self.currentGradingState = CurrentOperationState.fromDict(
            last[self.CURRENT_OPERATION_TABLENAME]
        )
        self.gradedSubmissions = set(last[self.GRADED_SUBMISSIONS])

        self.blacklistedSubmissions = set(
            last.get(self.BLACKLISTED_SUBMISSIONS, [])
        )


    def _checkpoint(self):
        self.progressLogger.logProgress({
            self.GRADING_SUMMARY_TABLENAME: dict(self.gradingSummary),
            self.CURRENT_OPERATION_TABLENAME: dict(self.currentGradingState),
            self.GRADED_SUBMISSIONS: list(self.gradedSubmissions),
            self.BLACKLISTED_SUBMISSIONS: list(self.blacklistedSubmissions)
        })


    def _refresh_monitor(self):
        self.monitor.updateTable(
            self.GRADING_SUMMARY_TABLENAME,
            self.gradingSummary
        )
        self.monitor.updateTable(
            self.CURRENT_OPERATION_TABLENAME,
            self.currentGradingState
        )
        self.monitor.refresh()

    # ----------------------------
    # Main grading loop
    # ----------------------------

    def grade(self):
        submissions = sorted(os.listdir(self.config["submissionsPath"]))
        self.gradingSummary.TotalSubmissions = len(submissions)

        for submission in submissions:
            if submission in self.gradedSubmissions:
                continue

            if submission in self.blacklistedSubmissions:
                continue

            with tempfile.TemporaryDirectory() as temp_dir:
                ctx = GradingContext(submission, temp_dir)

                self.currentGradingState.CurrentStudentFile = submission

                for step in self.pipeline:
                    step.run(ctx, self)
                    if ctx.fatal_error:
                        ctx.result.FatalErrors = ctx.fatal_error
                        break

                self.writer.writeTestResult(ctx.result)

                self.gradedSubmissions.add(submission)
                self.gradingSummary.SubmissionsGraded += 1

                if ctx.result.TestResults and all(t.Passed for t in ctx.result.TestResults):
                    self.gradingSummary.FullMarksSubmissionCount += 1

                self._checkpoint()
                self._refresh_monitor()

        self.monitor.stop()
