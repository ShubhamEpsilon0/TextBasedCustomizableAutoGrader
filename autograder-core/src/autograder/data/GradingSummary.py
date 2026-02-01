from dataclasses import dataclass, field
from autograder.data.DictMixin import DictMixin

@dataclass
class GradingSummary(DictMixin):
    TotalSubmissions: int = field(metadata={"alias":"📦 Total Submissions to be Graded"}, default=0)
    SubmissionsGraded: int = field(metadata={"alias":"🧮 Submissions Graded"}, default=0)
    TestCasesPassed: int = field(metadata={"alias":"✅ Total Test Cases Passed"}, default=0)
    TestCasesFailed: int = field(metadata={"alias":"❌ Total Test Cases Failed"}, default=0)
    SkippedSubmissions: int = field(metadata={"alias":"⏭️  Skipped Submissions"}, default=0)
    FullMarksSubmissionCount: int =  field(metadata={"alias":"🏆 Submissions Full Marks Count"}, default=0)