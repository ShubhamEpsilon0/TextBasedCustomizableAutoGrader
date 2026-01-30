from autograder.engine.PipelineStep import PipelineStep
from autograder.script_runner.CleanupRunner import CleanupRunner

class CleanupStep(PipelineStep):
    def __init__(self, phase: str):
        self.phase = phase  # "after_test" | "after_submission"

    def run(self, ctx, grader):
        cleanup_cfg = grader.config.get("cleanup")
        if not cleanup_cfg:
            return

        script = cleanup_cfg.get(self.phase)
        if not script:
            return

        grader.currentGradingState.CurrentOperation = f"Cleanup ({self.phase})"
        grader._refresh_monitor()

        runner = CleanupRunner(script)
        success, output = runner.clean(ctx.workspace)

        if not success:
            ctx.fatal_error = f"Cleanup failed ({self.phase})"
            ctx.result.SubmissionError = output

            grader.blacklistedSubmissions.add(ctx.submission_file)
            grader.gradingSummary.SkippedSubmissions += 1
