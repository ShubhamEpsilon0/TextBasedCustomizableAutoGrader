from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class TestResult:
    TestName: str
    Passed: bool
    Output: Optional[str]
    SimilarityReport: Optional[object]
    Error: Optional[str]

@dataclass
class ResultObject:
    StudentName: str = field(default_factory=str)
    AsuId: str = field(default_factory=str)
    FatalErrors: str = field(default_factory=str)
    StructureErrors: List[str] = field(default_factory=list)
    SubmissionError: str = field(default_factory=str)
    FinalScore: int = field(default_factory=int)
    TestResults: List[TestResult] = field(default_factory=list)
