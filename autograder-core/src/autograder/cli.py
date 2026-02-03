import argparse
import json
from autograder.engine.Grader import AutoGrader
from autograder.data.FolderStructure import FolderStructureData, FileType

def mapFileType(fileTypeInt):
    if fileTypeInt == 0:
        return FileType.FOLDER
    elif fileTypeInt == 1:
        return FileType.FILE
    else:
        raise ValueError(f"Unknown file type integer: {fileTypeInt}")

def parseFolderStructure(folderStructure):
    folderStructureData = []

    for item in folderStructure:
        folderStruct = FolderStructureData(item["fileName"], mapFileType(item["fileType"]))
        if mapFileType(item["fileType"]) == FileType.FOLDER:
            folderStruct.Content = parseFolderStructure(item["content"])
        else:
            folderStruct.misnomers = item.get("misnomers", [])
        folderStructureData.append(folderStruct)

    return folderStructureData

def parseConfig(configPath):
    with open(configPath) as f:
        config = json.load(f)

    if "folderStructure" in config:
        config["folderStructure"] = parseFolderStructure(config["folderStructure"])

    return config


def main():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--config", required=True)
        args = parser.parse_args()

        config = parseConfig(args.config)

        grader = AutoGrader(config)
        
        grader.grade()

    # grader.finalize()
    except Exception as e:
        print("Autograder encountered a fatal error:", e)
    finally:
        input("Press Enter to Exit..")
    

