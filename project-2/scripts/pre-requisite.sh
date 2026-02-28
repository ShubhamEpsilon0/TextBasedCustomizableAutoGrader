#!/bin/sh

build_dir="./process_gen"
if [ ! -d "$build_dir" ]; then
    echo "Error: Build directory not found: $build_dir"
    exit 1
fi

pushd "$build_dir"
    make clean
    make >/dev/null
popd 

# --- Setup user ---
name="test_cse330"
home_dir="/home/$name"

useradd "$name" 
mkdir -p "$home_dir" 
chmod 755 /home || true
chown -R "$name" "$home_dir" 
chmod 700 "$home_dir" || true

# --- Ensure /dev/null exists ---
if [ ! -c /dev/null ]; then
  mknod -m 666 /dev/null c 1 3 
fi