from autograder.engine.PipelineStep import PipelineStep

class BuildStep(PipelineStep):
    def run(self, ctx, grader):
        try:
            if not grader.config["testConfig"]["buildScriptPath"] or not grader.config["testConfig"]["buildTestRunnerType"]:
                return

            grader.currentGradingState.CurrentOperation = "Building Submission"
            grader._refresh_monitor()
            runner = grader.scriptRunners[grader.config["testConfig"]["buildTestRunnerType"]]

            success, out, err = runner.build(ctx.workspace)

            if not success:
                ctx.result.BuildPassed = False
                ctx.result.BuildError = err
                #ctx.result.SubmissionError = out + "\n" + err
                #grader.gradingSummary.SkippedSubmissions += 1
            else:
                ctx.result.BuildPassed = True
        except Exception as e:
            print(e)
            ctx.result.BuildPassed = False
            ctx.result.BuildError = str(e)
            grader.gradingSummary.SkippedSubmissions += 1
            
