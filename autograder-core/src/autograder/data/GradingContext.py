from dataclasses import dataclass, field
from autograder.data.ResultData import ResultObject

@dataclass
class GradingContext:
    submission_file: str
    workspace: str

    student_id: str = ""
    student_name: str = ""

    result: ResultObject = field(default_factory=ResultObject)

    fatal_error: str | None = None