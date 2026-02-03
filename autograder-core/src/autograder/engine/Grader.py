import os
import tempfile

from autograder.submissionsManager.SubmissionManager import SubmissionManager
from autograder.data.CurrentOperationState import CurrentOperationState
from autograder.script_runner.ShellScriptTestRunner import ShellScriptTestRunner
from autograder.script_runner.PythonTestRunner import PythonTestRunner
from autograder.result_writer.ExcelResultWriter import ExcelResultWriter

from autograder.data.GradingContext import GradingContext
from autograder.data.GradingSummary import GradingSummary
from autograder.data.StepLatency import StepLatency

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

from autograder.utils.timerContext import step_timer

class AutoGrader:
    GRADING_SUMMARY_TABLENAME = "Grading Summary"
    CURRENT_OPERATION_TABLENAME = "Current Operation State"
    STEP_LATENCY_TABLENAME = "Step Latencies"
    GRADED_SUBMISSIONS = "Graded Submissions"
    BLACKLISTED_SUBMISSIONS = "Blacklisted Submissions"

    def __init__(self, config: dict):
        self.blacklistedSubmissions = set()
        self.config = config
        self.resumeLogArea = "./logs/gradedLogs.json"
        self.logger = Logger("./logs/operationalLogs.log")

        self._initialize_script_runners()
        self._initialize_result_writer()
        self._initialize_monitoring()
        self._initialize_progress_logger()
        self._initialize_submission_manager()

        self._setup_pipeline()

    # ----------------------------
    # Main grading loop
    # ----------------------------

    def grade(self):
        try:
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
                        with step_timer(self.stepLatencies, step.__class__.__name__, self.gradingSummary.SubmissionsGraded + 1):
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
        except SystemExit as e:
            self.blacklistedSubmissions.add(self.currentGradingState.CurrentStudentFile)
            self._checkpoint()
            self.logger.error({
                "Component": "AutoGrader",
                "Operation": "grade",
                "Message": f"Grading halted due to fatal error: {str(e)}"
            })
            print("Grading halted due to fatal error. Check logs for details. Current Submission will be blacklisted..")
        except Exception as e:
            self.blacklistedSubmissions.add(self.currentGradingState.CurrentStudentFile)
            self._checkpoint()
            self.logger.error({
                "Component": "AutoGrader",
                "Operation": "grade",
                "Message": f"Grading halted due to fatal error: {str(e)}"
            })

    # ----------------------------
    # Private Functions
    # ----------------------------

    def _initialize_result_writer(self):
        self.writer = ExcelResultWriter(self.config["resultsFilePath"])
        self.writer.InitializeWriter()

    def _initialize_script_runners(self):
        buildScript = self.config["testConfig"].get("buildScriptPath")
        #Todo: Fix this
        #buildRunnerType = self.config["testConfig"].get("buildTestRunnerType
        self.scriptRunners = {
            "ShellScript": ShellScriptTestRunner(self.logger, buildScript, self.config.get("fatalErrors", []), self.config.get("placeholderRegex", {})),
            "Python": PythonTestRunner(self.logger, self.config.get("fatalErrors", []), self.config.get("placeholderRegex", {}))
        }

    def _initialize_monitoring(self):
        self.gradingSummary = GradingSummary()
        self.currentGradingState = CurrentOperationState()
        self.stepLatencies = StepLatency()
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
        self.monitor.addTable(
            self.STEP_LATENCY_TABLENAME,
            DictTableBuilder(self.STEP_LATENCY_TABLENAME, ["Step", "Avg. Latency (ms)"])
        )

        self.monitor.start()

    def _initialize_progress_logger(self):
        self.progressLogger = ProgressLogger(self.resumeLogArea)
        self._load_progress()
        self.progressLogger.InitializeForLogging()

    def _initialize_submission_manager(self):
        self.submissionManager = SubmissionManager(self.config, self.logger)

    def _setup_pipeline(self):
        self.pipeline = [
            ExtractSubmissionStep(),
            ParseStudentInfoStep(),
            LateSubmissionStep(),
            StructureValidationStep(),
            CopyDefaultFilesStep(),
            BuildStep(),
            RunTestsStep(),
            # CleanupStep()
        ]

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
        self.monitor.updateTable(
            self.STEP_LATENCY_TABLENAME,
            self.stepLatencies
        )
        self.monitor.refresh()
