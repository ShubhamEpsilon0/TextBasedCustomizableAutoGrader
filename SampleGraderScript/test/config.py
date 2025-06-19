from autograder.scripts.SubmissionManager import FolderStructureData, FileType

fatalErros = [
    "❌ Make Install Failed"
]

testConfig = {
    "MakeFilePath": "./test/copyableFiles/Makefile",
    "fatalErrors": fatalErros,
    "roosterPath": "./studentNames.txt",
    "loggingOn": False,
    "folderStructure": [
        FolderStructureData("kmodule", FileType.FOLDER, [
            FolderStructureData("Makefile", FileType.MAKEFILE),
            FolderStructureData("kmod-ioctl.c", FileType.C),
            FolderStructureData("kmod-main.c", FileType.C),
        ]),
        FolderStructureData("ioctl-defines.h", FileType.H),
    ],
    "submissionPath": "./submissions/",
    "testConfig": {
        "runScriptPath": "./test/run.sh",
        "buildScriptPath": "./test/build.sh",
        "testCases": [
            {
                "TestName": "TestRead",
                "intputLine": "./test/testcases/TestReadInput.txt",
                "expectedOutputFilePath": "./test/testcases/TestReadOutput.txt",
                "maxTestScore": 15
            },
            {
                "TestName": "TestWrite",
                "intputLine": "./test/testcases/TestWriteInput.txt",
                "expectedOutputFilePath": "./test/testcases/TestWriteOutput.txt",
                "maxTestScore": 15
            },
            {
                "TestName": "TestReadVar512-1-0",
                "intputLine": "./test/testcases/TestReadVar512-1-0Input.txt",
                "expectedOutputFilePath": "./test/testcases/TestReadVar512-1-0Output.txt",
                "maxTestScore": 5
            },
            {
                "TestName": "TestWriteVar512-1-0",
                "intputLine": "./test/testcases/TestWriteVar512-1-0Input.txt",
                "expectedOutputFilePath": "./test/testcases/TestWriteVar512-1-0Output.txt",
                "maxTestScore": 5
            },
            {
                "TestName": "TestReadVar512-1024-0",
                "intputLine": "./test/testcases/TestReadVar512-1024-0Input.txt",
                "expectedOutputFilePath": "./test/testcases/TestReadVar512-1024-0Output.txt",
                "maxTestScore": 5
            },
            {
                "TestName": "TestWriteVar512-100000-0",
                "intputLine": "./test/testcases/TestWriteVar512-100000-0Input.txt",
                "expectedOutputFilePath": "./test/testcases/TestWriteVar512-100000-0Output.txt",
                "maxTestScore": 5
            },
            {
                "TestName": "TestReadVar2048-100000-0",
                "intputLine": "./test/testcases/TestReadVar2048-100000-0Input.txt",
                "expectedOutputFilePath": "./test/testcases/TestReadVar2048-100000-0Output.txt",
                "maxTestScore": 5
            },
            {
                "TestName": "TestWriteVar8192-100000-0",
                "intputLine": "./test/testcases/TestWriteVar8192-100000-0Input.txt",
                "expectedOutputFilePath": "./test/testcases/TestWriteVar8192-100000-0Output.txt",
                "maxTestScore": 5
            },
            {
                "TestName": "TestReadVar16384-100000-0",
                "intputLine": "./test/testcases/TestReadVar16384-100000-0Input.txt",
                "expectedOutputFilePath": "./test/testcases/TestReadVar16384-100000-0Output.txt",
                "maxTestScore": 5
            },
            {
                "TestName": "TestWriteVar131072-768-0",
                "intputLine": "./test/testcases/TestWriteVar131072-768-0Input.txt",
                "expectedOutputFilePath": "./test/testcases/TestWriteVar131072-768-0Output.txt",
                "maxTestScore": 5
            },
            {
                "TestName": "TestReadVar512-100000-131072",
                "intputLine": "./test/testcases/TestReadVar512-100000-131072Input.txt",
                "expectedOutputFilePath": "./test/testcases/TestReadVar512-100000-131072Output.txt",
                "maxTestScore": 5
            },
            {
                "TestName": "TestWriteVar2048-100000-16384",
                "intputLine": "./test/testcases/TestWriteVar2048-100000-16384Input.txt",
                "expectedOutputFilePath": "./test/testcases/TestWriteVar2048-100000-16384Output.txt",
                "maxTestScore": 5
            },
            {
                "TestName": "TestReadVar16384-100000-1048576",
                "intputLine": "./test/testcases/TestReadVar16384-100000-1048576Input.txt",
                "expectedOutputFilePath": "./test/testcases/TestReadVar16384-100000-1048576Output.txt",
                "maxTestScore": 5
            },
            {
                "TestName": "TestReadVar8192-100-134217728",
                "intputLine": "./test/testcases/TestReadVar8192-100-134217728Input.txt",
                "expectedOutputFilePath": "./test/testcases/TestReadVar8192-100-134217728Output.txt",
                "maxTestScore": 5
            },
            {
                "TestName": "TestWriteVar8192-512-402653184",
                "intputLine": "./test/testcases/TestWriteVar8192-512-402653184Input.txt",
                "expectedOutputFilePath": "./test/testcases/TestWriteVar8192-512-402653184Output.txt",
                "maxTestScore": 5
            },
            {
                "TestName": "TestWriteVar393216-1024-402653184",
                "intputLine": "./test/testcases/TestWriteVar393216-1024-402653184Input.txt",
                "expectedOutputFilePath": "./test/testcases/TestWriteVar393216-1024-402653184Output.txt",
                "maxTestScore": 5
            },
        ]
    },
    "resultsFilePath": "./results-test7.xlsx"
}
