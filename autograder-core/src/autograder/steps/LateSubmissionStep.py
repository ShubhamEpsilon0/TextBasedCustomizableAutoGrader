from autograder.engine.PipelineStep import PipelineStep

class LateSubmissionStep(PipelineStep):
    def run(self, ctx, grader):
        if grader.submissionManager.checkForLateSubmission(ctx.submission_file):
            ctx.fatal_error = "Late Submission"
            ctx.result.SubmissionError = "Late Submission"
            grader.gradingSummary.SkippedSubmissions += 1
