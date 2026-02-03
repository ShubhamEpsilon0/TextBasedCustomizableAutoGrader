from dataclasses import dataclass, field
from autograder.data.DictMixin import DictMixin

@dataclass
class CurrentOperationState(DictMixin):
    CurrentStudentFile: str = field(metadata={"alias":"Current Student File"}, default="")
    CurrentOperation: str = field(metadata={"alias":"Current Operation"}, default="")