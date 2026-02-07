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

# Navigate to the kernel_module directory inside the submission path using pushd
SYSCALL_FILE_PATH="$SUBMISSION_PATH/cse330-kernel-files-project1/my_syscall"

if [ ! -d "$SYSCALL_FILE_PATH" ]; then
    echo "Error: The 'kernel_module' directory does not exist inside the submission path." >&2
    exit 1
fi

# Use pushd to change to the kernel_module directory, suppress output
pushd "$SYSCALL_FILE_PATH" > /dev/null || exit

out=$(grep -Ei "hello.*i am .*student.*cse330.*fall.*2025" *.c)

# Check if "hello" was found in the dmesg log
if [ $? -eq 0 ]; then
    # If found, print "Success" along with the message
    echo $out
    echo "Success: 'hello' found in dmesg log."
else
    # If not found, print the last 5 lines of the dmesg log and "Failure"
    echo "Failure: 'hello' not found in dmesg log. Error => $out" >&2
    sudo dmesg | tail -n 5 >&2
fi

# Return to the previous directory using popd, suppress output
popd > /dev/null

exit 0

