#!/bin/bash

cleanup() {
    sudo dmesg -C
    sudo rmmod memalloc 2>/dev/null || true
}

trap cleanup EXIT

if [ $# -ne 2 ]; then
    echo "Error: Usage: $0 <submission_path> <testcase_name>" >&2
    exit 1
fi

path_to_submission_folder=$1
testcase_name=$2
# cleanup

# Install Kernel Module
pushd "$path_to_submission_folder/memalloc" > /dev/null || exit

out=$(sudo insmod memalloc.ko 2>&1) || KERNEL_MODULE_ERR="$out"

if [ -n "$KERNEL_MODULE_ERR" ]; then
    echo -e "[log]: ─ Failed to insert kernel module: ${KERNEL_MODULE_ERR}" >&2
    exit 1
fi

popd > /dev/null

# Run Test Case
pushd "$path_to_submission_folder/testcases" > /dev/null || exit
if [ ! -f "$testcase_name" ]; then
    echo "Error: Test case '$testcase_name' not found in the testcases directory." >&2
    exit 1
fi

./"$testcase_name"

sudo dmesg | tail -n 10

popd > /dev/null


#remove kernel module

out=$(sudo rmmod memalloc 2>&1) || KERNEL_MODULE_ERR="$out"

if [ -n "$KERNEL_MODULE_ERR" ]; then
    echo -e "[log]: ─ Failed to remove kernel module: ${KERNEL_MODULE_ERR}" >&2
    exit 1
fi

exit 0
