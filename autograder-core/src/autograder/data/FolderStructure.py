from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

from autograder.data.DictMixin import DictMixin

class FileType(Enum):
    FOLDER = 0
    FILE = 1


# FILE_TYPE_EXTENSIONS = {
#     FileType.PNG: ".png",
#     FileType.TXT: ".txt",
#     FileType.C: ".c",
#     FileType.CPP: ".cpp",
#     FileType.JPEG: ".jpeg",
#     FileType.MAKEFILE: "",
#     FileType.H: ".h",
#     FileType.TBL: ".tbl",
# }

@dataclass
class FolderStructureData(DictMixin):
    fileName: str = field(default_factory=str)
    fileType: FileType = field(default=FileType.FOLDER)
    Content: Optional[List['FolderStructureData']] = field(default_factory=list)
    misnomers: List[str] = field(default_factory=list)
