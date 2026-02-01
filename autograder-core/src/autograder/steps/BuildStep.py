from autograder.engine.PipelineStep import PipelineStep

class BuildStep(PipelineStep):
    def run(self, ctx, grader):
        if not grader.config["testConfig"]["buildScriptPath"] or not grader.config["testConfig"]["buildTestRunnerType"]:
            return

        grader.currentGradingState.CurrentOperation = "Building Submission"
        grader._refresh_monitor()
        runner = grader.scriptRunners[grader.config["testConfig"]["buildTestRunnerType"]]

        success, out, err = runner.build(ctx.workspace)

        if not success:
            ctx.fatal_error = "Build failed"
            ctx.result.SubmissionError = out + "\n" + err
            grader.gradingSummary.SkippedSubmissions += 1
