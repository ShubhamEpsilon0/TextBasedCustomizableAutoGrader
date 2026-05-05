#!/bin/bash

# Check if submission path is provided as the first argument
if [ -z "$1" ]; then
    echo "Error: Submission path is required as the first argument." >&2
    exit 1
fi

# Assign the submission path from the argument
SUBMISSION_PATH="$1"

# Check if the submission path exists
if [ ! -d "$SUBMISSION_PATH" ]; then
    echo "Error: The provided submission path does not exist." >&2
    exit 1
fi

# Navigate to the kmodule directory inside the submission path using pushd
SOURCE_CODE_PATH="$SUBMISSION_PATH/kmodule"
if [ ! -d "$SOURCE_CODE_PATH" ]; then
    echo "Error: The 'kmodule' directory does not exist inside the submission path." >&2
    exit 1
fi

# Use pushd to change to the source_code directory, suppress output
pushd "$SUBMISSION_PATH" > /dev/null || exit

    pushd "kmodule" > /dev/null || exit
        # Check if Makefile exists in the source_code directory
        if [ ! -f "Makefile" ]; then
            echo "Error: Makefile not found in the source_code directory." >&2
            # Return to the previous directory using popd, suppress output
            popd > /dev/null
            exit 1
        fi

        # Compile the kernel module using the Makefile, suppress all output
        #make > /dev/null 2>&1
        make clean > /dev/null 2>&1
        out=$(make)

        # Check if the compilation was successful
        if [ $? -ne 0 ]; then
            echo "Error: Kernel module compilation failed. Error => $out" >&2
            popd > /dev/null
            exit 1
        fi

    # Return to the previous directory using popd, suppress output
    popd > /dev/null

    # Compile Test Cases
    pushd "testcases" > /dev/null || exit
        testcases=("read" "write" "read-variable" "write-variable")
        rm -rf *.txt
        make clean

        for testcase in "${testcases[@]}"; do
            make "test-$testcase"
        done
    popd > /dev/null

popd > /dev/null

exit 0

