#!/bin/bash -e 

out=""
if [ "$#" -lt 1 ];
then
    echo "Usage: ./test.sh <name>"
    echo "Usage:        E.g., ./test.sh read"
    exit 0
fi

out=$out"$1"
if [[ $1 == *"-variable" ]]; then
    if [ "$#" -lt 4 ];
    then
        echo "Usage: ./test.sh $1 <blocksize> <iterations> <offset>"
        echo "Usage:        E.g., ./test.sh test-read-variable 512 1000 0"
        exit 0
    fi
    out=$out"-$2-$3-$4"
fi

# Check which /dev entry contains the USB device
dpath=/dev/`lsblk | grep 4G | cut -d ' ' -f 1`

mkdir -p $1/test/testcases || true
cp -r ../test/testcases $1/test/

pushd $1 > /dev/null 2>&1
pushd kmodule > /dev/null 2>&1
    make  > /dev/null 2>&1 || { echo "❌ Make Failed"; exit 1; }
    make remove > /dev/null 2>&1 || true
	sudo insmod kmod.ko device=$dpath || { echo "❌ Make Install Failed"; exit 1; }
popd > /dev/null 2>&1

# Run a testcase
pushd test/testcases > /dev/null 2>&1
    rm -rf *.txt >  /dev/null 2>&1
    make clean > /dev/null 2>&1 || true
    make test-$2 > /dev/null 2>&1 || { echo "❌ Make Test Failed"; exit 1; }
    sudo ./test-$2 $dpath $3 $4 $5
popd > /dev/null 2>&1
popd > /dev/null 2>&1
