import os
from autograder.engine.PipelineStep import PipelineStep

class ExtractSubmissionStep(PipelineStep):
    def run(self, ctx, grader):
        try:
            grader.currentGradingState.CurrentOperation = "Extracting Submission"
            grader._refresh_monitor()

            zip_path = os.path.join(grader.config["submissionsPath"], ctx.submission_file)

            if not grader.submissionManager.extractSubmissions(zip_path, ctx.workspace):
                ctx.fatal_error = "Extraction failed"
                ctx.result.SubmissionError = ctx.fatal_error
                grader.gradingSummary.SkippedSubmissions += 1

        except Exception as e:
            ctx.fatal_error = "Exception in Extract Submission Step : " + str(e)
            ctx.result.SubmissionError = ctx.fatal_error
            grader.gradingSummary.SkippedSubmissions += 1
