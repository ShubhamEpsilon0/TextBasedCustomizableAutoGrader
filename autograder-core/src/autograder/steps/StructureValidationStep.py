from autograder.engine.PipelineStep import PipelineStep

class StructureValidationStep(PipelineStep):
    def run(self, ctx, grader):
        grader.currentGradingState.CurrentOperation = "Validating Folder Structure"
        grader._refresh_monitor()

        report = grader.submissionManager.validateStructure(ctx.workspace)
        ctx.result.StructureErrors = report

        if report["missing"]:
            try:
                grader.submissionManager.safelyFixFolderStructure(ctx.workspace)
            except:
                ctx.fatal_error = "Invalid folder structure"
                grader.gradingSummary.SkippedSubmissions += 1
