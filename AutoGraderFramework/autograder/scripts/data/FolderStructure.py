from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

from autograder.scripts.data.DictMixin import DictMixin

class FileType(Enum):
    FOLDER = 0
    PNG = 1,
    TXT = 2,
    C   = 3,
    CPP = 4,
    JPEG = 5,
    MAKEFILE = 6,
    H = 7


FILE_TYPE_EXTENSIONS = {
    FileType.PNG: ".png",
    FileType.TXT: ".txt",
    FileType.C: ".c",
    FileType.CPP: ".cpp",
    FileType.JPEG: ".jpeg",
    FileType.MAKEFILE: "",
    FileType.H: ".h"
}

@dataclass
class FolderStructureData(DictMixin):
    fileName: str
    fileType: FileType
    Content: Optional[List['FolderStructureData']] = field(default_factory=list)
