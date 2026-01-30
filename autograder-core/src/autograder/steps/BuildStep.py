from autograder.engine.PipelineStep import PipelineStep

class BuildStep(PipelineStep):
    def run(self, ctx, grader):
        if not grader.config["testConfig"]["buildScriptPath"]:
            return

        grader.currentGradingState.CurrentOperation = "Building Submission"
        grader._refresh_monitor()

        success, out, err = grader.testRunner.build(ctx.workspace)

        if not success:
            ctx.fatal_error = "Build failed"
            ctx.result.SubmissionError = out + "\n" + err
            grader.gradingSummary.SkippedSubmissions += 1
