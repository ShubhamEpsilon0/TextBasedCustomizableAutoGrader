#!/bin/bash -e 

if [ "$#" -lt 1 ];
then
    echo "Usage: ./test.sh <Student Submission Path>"
    echo "Usage:        E.g., ./test.sh read"
    exit 0
fi

# Check which /dev entry contains the USB device
dpath=/dev/`lsblk | grep 1G | cut -d ' ' -f 1`

pushd $1 > /dev/null 2>&1
pushd kmodule > /dev/null 2>&1
    make  > /dev/null 2>&1 || { echo "❌ Make Failed"; exit 1; }
    make remove > /dev/null 2>&1 || true
	sudo insmod kmod.ko device=$dpath || { echo "❌ Make Install Failed"; exit 1; }
popd > /dev/null 2>&1
popd > /dev/null 2>&1
