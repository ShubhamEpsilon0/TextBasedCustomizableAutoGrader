#!/bin/bash

cleanup() {
    sudo dmesg -C > /dev/null 2>&1

    local dname
    dname=$(lsblk -ndo NAME,SIZE,TYPE | awk '$2=="1G" && $3=="disk" {print $1; exit}')
    [ -n "$dname" ] || { echo "No matching 1G disk found"; exit 1; }

    local dpath
    dpath="/dev/$dname"
    [ -b "$dpath" ] || { echo "Not a block device: $dpath"; exit 1; }

    echo "$dname" "$dpath"
    # local size
    set -o pipefail
    
    # dd if=/dev/zero of="$dpath" bs=16M status=none conv=fsync
    # sync
    # blockdev --flushbufs "$dpath"

    size=$(blockdev --getsize64 "$dpath")
    if ! dd if=/dev/zero of="$dpath" bs=1M count=$(( size / 1024 / 1024 )) status=none; then
        echo "dd failed (real error)" >&2
        exit 1
    fi

    sudo rmmod kmod 2>/dev/null || true
}

trap cleanup EXIT

if [ "$#" -lt 2 ];
then
    echo "Error: No arguments provided. Usage: $0 <submission_path> <test-name>" >&2
    exit 0
fi


path_to_submission_folder=$1
testcase_name=$2
blocksize=
iterations=
offset=

if [[ $2 == *"-variable" ]]; then
    if [ $# -ne 5 ]; then
        echo "Error: Usage: $0 <submission_path> <test-name> <blocksize> <iterations> <offset>" >&2
        exit 1
    fi

    blocksize=$3
    iterations=$4
    offset=$5
fi



if [ $testcase_name == "write" ] || [ $testcase_name == "write-variable" ]; then
    cleanup
    sleep 3
fi

dname=$(lsblk -ndo NAME,SIZE,TYPE | awk '$2=="1G" && $3=="disk" {print $1; exit}')
[ -n "$dname" ] || { echo "No matching 1G disk found"; exit 1; }

dpath="/dev/$dname"
[ -b "$dpath" ] || { echo "Not a block device: $dpath"; exit 1; }

# Install Kernel Module
pushd "$path_to_submission_folder/kmodule" > /dev/null || exit

out=$(sudo insmod kmod.ko device=$dpath 2>&1) || KERNEL_MODULE_ERR="$out"

if [ -n "$KERNEL_MODULE_ERR" ]; then
    echo -e "[log]: ─ Failed to insert kernel module: ${KERNEL_MODULE_ERR}" >&2
    exit 1
fi

sudo chmod 666 /dev/kmod || { echo "Error: Failed to set permissions on /dev/kmod" >&2; exit 1; }

popd > /dev/null

# Run Test Case
pushd "$path_to_submission_folder/testcases" > /dev/null || exit
    if [ ! -f "test-$testcase_name" ]; then
        echo "Error: Test case 'test-$testcase_name' not found in the testcases directory." >&2
        exit 1
    fi

    lsmod | grep kmod || { echo "Error: Kernel module 'kmod' is not loaded." >&2; exit 1; }

    rm -rf *.txt

    ./"test-$testcase_name" $dpath $blocksize $iterations $offset

    if [ $? -ne 0 ]; then
        echo "Error: Test case '$testcase_name' execution failed." >&2
        rm -rf *.txt
        popd > /dev/null
        exit 1
    fi

    rm -rf *.txt

popd > /dev/null

#remove kernel module
out=$(sudo rmmod kmod 2>&1) || KERNEL_MODULE_ERR="$out"

if [ -n "$KERNEL_MODULE_ERR" ]; then
    echo -e "[log]: ─ Failed to remove kernel module: ${KERNEL_MODULE_ERR}" >&2
    exit 1
fi

exit 0
