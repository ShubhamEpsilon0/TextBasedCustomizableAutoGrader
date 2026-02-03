from autograder.engine.PipelineStep import PipelineStep

class ParseStudentInfoStep(PipelineStep):
    def run(self, ctx, grader):
        try:
            grader.currentGradingState.CurrentOperation = "Parsing Student Info"
            grader._refresh_monitor()

            info = grader.submissionManager.parseASUIdAndStudentNameFromFilename(
                ctx.submission_file
            )
            ctx.student_id = info["asu_id"]
            ctx.student_name = info["name"]

            ctx.result.AsuId = ctx.student_id
            ctx.result.StudentName = ctx.student_name

        except ValueError as e:
            ctx.fatal_error = "Parsing Error: " + str(e)
            ctx.result.SubmissionError = ctx.fatal_error
            grader.gradingSummary.SkippedSubmissions += 1
        except Exception as e:
            ctx.fatal_error = "Exception in Parse Student Info Step : " + str(e)
            ctx.result.SubmissionError = ctx.fatal_error
            grader.gradingSummary.SkippedSubmissions += 1
