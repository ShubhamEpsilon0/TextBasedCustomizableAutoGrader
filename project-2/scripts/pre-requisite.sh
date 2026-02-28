#!/bin/bash

build_dir="./process_gen"
if [ ! -d "$build_dir" ]; then
    echo "Error: Build directory not found: $build_dir"
    exit 1
fi

pushd "$build_dir"
    make clean
    make
popd 

# --- Setup user ---
name="test_cse330"
home_dir="/home/$name"

useradd "$name" 
mkdir -p "$home_dir" 
sudo chmod 755 /home || true
sudo chown -R "$name" "$home_dir" 
sudo chmod 700 "$home_dir" || true

# Copy Process Gen to User
sudo cp $build_dir/process_generator "$home_dir/"
sudo chown "$name:$name" "$home_dir/process_generator"
sudo chmod 700 "$home_dir/process_generator"

# --- Ensure /dev/null exists ---
if [ ! -c /dev/null ]; then
  sudo mknod -m 666 /dev/null c 1 3 
fi
