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
KERNEL_MODULE_PATH="$SUBMISSION_PATH/kernel_module"

if [ ! -d "$KERNEL_MODULE_PATH" ]; then
    echo "Error: The 'kernel_module' directory does not exist inside the submission path." >&2
    exit 1
fi

# Use pushd to change to the kernel_module directory, suppress output
pushd "$KERNEL_MODULE_PATH" > /dev/null || exit

# Check if the module is currently loaded using lsmod
MODULE_NAME="my_name.ko"
if lsmod | grep -q "$MODULE_NAME"; then
    # Force remove the kernel module if it is still loaded
    rmmod -f "$MODULE_NAME" > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "Error: Failed to force remove the kernel module." >&2
        # Return to the previous directory using popd, suppress output
        popd > /dev/null
        exit 1
    fi
fi


# Return to the previous directory using popd, suppress output
popd > /dev/null

exit 0

