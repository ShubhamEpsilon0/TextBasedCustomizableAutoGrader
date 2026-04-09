#!/bin/bash

cleanup() {
    sudo dmesg -C
    # Check which /dev entry contains the USB device
    dpath=/dev/`lsblk | grep " 1G " | cut -d ' ' -f 1`

    # Make sure the /dev entries are present
    ([ ! -e "$dpath" ] && sudo mount -t devtmpfs devtmpfs /dev) || true

    # Cleaning the device
    SIZE=$(sudo blockdev --getsize64 "$dpath") || exit
    sudo dd if=/dev/zero of="$dpath" bs=1M count=$(( SIZE / 1024 / 1024 )) || exit 

    # Remove the module if it is present
    sudo rmmod kmod 2>/dev/null || true
}

trap cleanup EXIT

if [ $# -ne 5 ]; then
    echo "Error: Usage: $0 <submission_path> <test-name> <blocksize> <iterations> <offset>" >&2
    exit 1
fi

path_to_submission_folder=$1
testcase_name=$2
blocksize=$3
iterations=$4
offset=$5

cleanup

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
if [ ! -f "test-$testcase_name" ]; then
    echo "Error: Test case 'test-$testcase_name' not found in the testcases directory." >&2
    exit 1
fi

./"test-$testcase_name" $blocksize $iterations $offset
if [ $? -ne 0 ]; then
    echo "Error: Test case '$testcase_name' execution failed." >&2
    popd > /dev/null
    exit 1
fi
popd > /dev/null

#remove kernel module
out=$(sudo rmmod memalloc 2>&1) || KERNEL_MODULE_ERR="$out"

if [ -n "$KERNEL_MODULE_ERR" ]; then
    echo -e "[log]: ─ Failed to remove kernel module: ${KERNEL_MODULE_ERR}" >&2
    exit 1
fi

exit 0
