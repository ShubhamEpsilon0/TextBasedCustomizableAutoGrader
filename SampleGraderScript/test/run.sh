#!/bin/bash -e 

if [ "$#" -lt 2 ];
then
    echo "Usage: ./test.sh <name>"
    echo "Usage:        E.g., ./test.sh read"
    exit 0
fi

if [[ $1 == *"-variable" ]]; then
    if [ "$#" -lt 5 ];
    then
        echo "Usage: ./test.sh $1 <blocksize> <iterations> <offset>"
        echo "Usage:        E.g., ./test.sh test-read-variable 512 1000 0"
        exit 0
    fi
fi

# Check which /dev entry contains the USB device
dpath=/dev/`lsblk | grep 1G | cut -d ' ' -f 1`

mkdir -p $1/test/testcases || true
cp -r ../test/testcases $1/test/

pushd $1 > /dev/null 2>&1
pushd test/testcases > /dev/null 2>&1
    rm -rf *.txt >  /dev/null 2>&1
    make clean > /dev/null 2>&1 || true
    make test-$2 > /dev/null 2>&1 || { echo "❌ Make Test Failed"; exit 1; }
    sudo ./test-$2 $dpath $3 $4 $5
popd > /dev/null 2>&1
popd  > /dev/null 2>&1