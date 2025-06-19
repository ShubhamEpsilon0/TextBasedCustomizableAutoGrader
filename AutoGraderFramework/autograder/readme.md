Usage:

Expectations of files and folders:

1.  The Zipped file should not contain an enclosing folder. It should be in the format as downloaded from canvas.
    That is after extraction they shouldn't be inside a folder like submissions
2.  studentNames.txt should contain all the names of the student in proper form, refer to the StudentNames.txt in this folder.. These are the names that will appear in the result excel sheet.
3.  test folder contains all the test scripts and test cases that will be run for each submission. It also contains following important files3

- Config.py -> it allows you to provide some configuration to the Autograder like
  SubmissionsPath: path to the submissions.zip file
  ResultsFilePath: Path to the result excel file
  And Test Configurations including their input, output, expected output and marks associated with it. 4. logs: This allows for resumability of grading as there is a chance that some submission will cause the unloading of modules to fail, so the system will have to be restarted. GradedLogs file in this folder allows for resumption from last graded submission. Remember to delete this file for fresh start to get correct monitoring data displayed on screen

Result Excel Structure:

Student Name - from Student Names.txt and submission file name
Asu Id
Structure Errors
Submission Error -> In case there are unzipping errors or other project level errors including compilation errors
Final Score
Tests
For each test case
Passed - Bool to indicate test result.
Output - stdout will be available here
Error - Error while running test case - any stderr output will be available here
Similarity Report- Compares each line in output with each line in expected output to provide a report on why the test case failed. it gives you the best match for each line. therefore in cases of failure graders can refer to this report to identify if there is a genuine failure in which case they can avoid re-running the test case.

Suggestions for smooth Operation:

1. Try to break the submissions into multiple subsubmission folders as I faced issues where my VM got stuck and in some cases it resulted in loss of resume log which then required a full rerun.
2. In case there is a need for re-run keep an eye on the results excel file as the code will append to it even if it is regrading some inputs, so in case of re-grade scenario remember to delete the older entries.
3. Reach out in case of issues..
4. Run Test cases 3 and 7 separately as they have some conflicting memory allocations and running them together will cause them to fail. so run all the remaining test cases first, then just test case 3 and then test case 7. Finally merge the results manually.
