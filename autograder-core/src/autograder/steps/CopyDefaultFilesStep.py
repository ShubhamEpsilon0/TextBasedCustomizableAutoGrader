from autograder.engine.PipelineStep import PipelineStep

class CopyDefaultFilesStep(PipelineStep):
    def run(self, ctx, grader):
        if grader.submissionManager.copyDefaultFiles(ctx.workspace):
            ctx.fatal_error = "Unable to Copy Default Files"
            ctx.result.SubmissionError = "Unable to Copy Default Files"
            grader.gradingSummary.SkippedSubmissions += 1