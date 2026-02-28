#!/bin/bash

name="test_cse330"
uid=$(id -u "$name")
sudo dmesg -C >/dev/null 2>&1 || echo "Error: Clean up Failed" >&2
if pgrep -u "$uid" >/dev/null; then
    sudo pkill -u "$uid" >/dev/null 2>&1 || echo "Error: Clean up Failed" >&2
fi