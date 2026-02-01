import json
import os

from autograder.steps import CleanupStep
from autograder.engine.PipelineStep import PipelineStep
from autograder.data.ResultData import TestResult

class RunTestsStep(PipelineStep):
    def run(self, ctx, grader):
        for tc in grader.config["testConfig"]["testCases"]:
            grader.currentGradingState.CurrentOperation = f"Running {tc['testName']}"
            grader._refresh_monitor()

            runner = grader.scriptRunners[tc["testRunnerType"]]

            res = runner.run(
                ctx.workspace,
                os.path.join(grader.config["testFolderPath"], tc["testName"]),
                tc["inputLine"],
                os.path.join(grader.config["testFolderPath"],tc["testName"],tc["expectedOutputFilePath"],),
                os.path.join(grader.config["testFolderPath"],tc["testName"],tc["runScriptPath"],), 
            )

            ctx.result.TestResults.append(
                TestResult(
                    tc["testName"],
                    res["passed"],
                    res["output"],
                    json.dumps(res["similarity_report"]),
                    res["error"]
                )
            )

            if res["passed"]:
                grader.gradingSummary.TestCasesPassed += 1
                ctx.result.FinalScore += tc["maxTestScore"]
            else:
                grader.gradingSummary.TestCasesFailed += 1

            # CleanupStep("after_test").run(ctx, grader)

            if ctx.fatal_error:
                break
