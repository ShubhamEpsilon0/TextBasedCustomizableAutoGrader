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

# Insert the kernel module, suppressing output
out=$(sudo insmod my_name.ko 2>&1)

# Check if the module was inserted successfully
if [ $? -ne 0 ]; then
    echo "Error: Failed to insert the kernel module. Error => $out" >&2
    # Remove the kernel module in case of failure
    sudo rmmod my_name > /dev/null 2>&1
    popd > /dev/null
    exit 1
fi

# Search for "hello" in the dmesg log, suppressing other output
out=$(sudo dmesg | grep -i "hello" 2>&1) #> /dev/null 2>&1

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

#clean dmesg log
sudo dmesg -C

# Remove the kernel module, suppressing output
out=$(sudo rmmod my_name 2>&1)
if [ $? -ne 0 ]; then
    echo "Error: Failed to remove the kernel module. Error => $out" >&2
    # Remove the kernel module in case of failure
    sudo rmmod my_name > /dev/null 2>&1
    popd > /dev/null
    exit 1
fi




# Return to the previous directory using popd, suppress output
popd > /dev/null

exit 0

