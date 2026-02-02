from dataclasses import dataclass, field
from autograder.data.DictMixin import DictMixin

@dataclass
class StepLatency(DictMixin):
    ExtractSubmissionStep: float = field(metadata={"alias":"Extract Submission Step"}, default=0.0)
    ParseStudentInfoStep: float = field(metadata={"alias":"Parse Student Info"}, default=0.0)
    LateSubmissionStep: float = field(metadata={"alias":"Late Submission Step"}, default=0.0)
    StructureValidationStep: float = field(metadata={"alias":"Structure Validation Step"}, default=0.0)
    CopyDefaultFilesStep: float = field(metadata={"alias":"Copy Files Step"}, default=0.0)
    BuildStep: float = field(metadata={"alias":"Build Step"}, default=0.0)
    RunTestsStep: float = field(metadata={"alias":"Run Tests Step"}, default=0.0)
    CleanupStep: float = field(metadata={"alias":"Cleanup Step"}, default=0.0)