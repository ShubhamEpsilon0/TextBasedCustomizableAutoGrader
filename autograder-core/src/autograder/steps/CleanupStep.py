from autograder.engine.PipelineStep import PipelineStep
from autograder.script_runner.CleanupRunner import CleanupRunner

class CleanupStep(PipelineStep):
    def __init__(self, phase: str):
        self.phase = phase  # "after_test" | "after_submission"

    def run(self, ctx, grader):
        cleanup_cfg = grader.config["testConfig"].get("cleanupConfig", {})
        if not cleanup_cfg:
            return
        
        grader.currentGradingState.CurrentOperation = f"Cleaning Up Submission ${ctx.submission_file}"
        grader._refresh_monitor()

        cleanup_script = cleanup_cfg.get("cleanUpScriptPath")
        if not cleanup_script:
            return
        
        CleanUpScriptRunnerType = cleanup_cfg.get("cleanUpScriptRunnerType", "ShellScript")
        runner = grader.scriptRunners[CleanUpScriptRunnerType]
        success, output = runner.clean(cleanup_script)

        if not success:
            ctx.fatal_error = f"Cleanup failed. Error: {output}"