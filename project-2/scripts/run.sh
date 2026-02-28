#!/bin/bash

percent_diff_time() {
    local t1="$1"
    local t2="$2"

    # Convert HH:MM:SS to total seconds
    IFS=: read -r h1 m1 s1 <<< "$t1"
    IFS=: read -r h2 m2 s2 <<< "$t2"

    local total1=$((10#$h1*3600 + 10#$m1*60 + 10#$s1))
    local total2=$((10#$h2*3600 + 10#$m2*60 + 10#$s2))

    # Prevent division by zero
    if [ "$total1" -eq 0 ]; then
        echo "Time Check Failed"
        return 1
    fi

    # Absolute difference
    local diff=$(( total2 - total1 ))
    if [ "$diff" -lt 0 ]; then
        diff=$(( -diff ))
    fi

    # Compute percentage
    local percent=$(awk "BEGIN { print ($diff/$total1)*100 }")

    # Compare with threshold (20%)
    awk "BEGIN { exit !($percent < 20) }"
    if [ $? -eq 0 ]; then
        echo "Time Check Passed"
    else
        echo "Time Check Failed"
    fi
}


# --- Trap for cleanup on exit or error ---
cleanup() {
    name="test_cse330"
    uid=$(id -u "$name")
    sudo dmesg -C >/dev/null 2>&1 || echo "Error: Clean up Failed" >&2
    if pgrep -u "$uid" >/dev/null; then
        sudo pkill -u "$uid" >/dev/null 2>&1 || echo "Error: Clean up Failed" >&2
    fi
}
trap cleanup EXIT

# --- Check argument count ---
if [ $# -ne 6 ]; then
  echo "Error: Usage: $0  <submission_path> <num_processes> <buffer_size> <num_producers> <num_consumers> <dmesg_lines>" >&2
  exit 1
fi

path_to_build_script="$(cd "$(dirname "$0")" && pwd)"
path_to_kernel_module=$1
num=$2
buffSize=$3
prod=$4
cons=$5
dmesg_lines=$6


# --- Validate num_processes ---
if ! [[ "$num" =~ ^[0-9]+$ ]]; then
  echo "Error: <num_processes> must be a positive integer." >&2
  exit 1
fi

# --- Save num to file ---
name="test_cse330"
home_dir="/home/$name"
# --- Run process generator as the test user ---
uid=$(id -u "$name")
process_gen_path="$home_dir/process_generator"

#su "$name" -c "whoami && ls -l $process_gen_path"
su "$name" -c "$process_gen_path $num" >/dev/null 2>&1 &

#cmd="su \"$name\" -c \"$process_gen_path $num\""
#echo "Executing: $cmd"

pg_pid=$!
sleep 10

# --- Run ps_time.sh ---
ps_time_script="$path_to_build_script/ps_time.sh"
if [ ! -x "$ps_time_script" ]; then
    echo "Error: ps_time.sh not found: $ps_time_script" >&2
    exit 1
fi

ps_output=$(bash "$ps_time_script" "$uid" &)
# --- Insert kernel module ---
kernel_module="$path_to_kernel_module/kernel_module/producer_consumer.ko"
if [ ! -f "$kernel_module" ]; then
    echo "Error: Kernel module not found: $kernel_module" >&2
    exit 1
fi

sudo insmod "$kernel_module" buffSize="$buffSize" prod="$prod" cons="$cons" uuid="$uid" >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Failed to insert kernel module" >&2
    exit 1
fi

sleep 10

# --- Remove kernel module ---
sudo rmmod producer_consumer >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Failed to remove kernel module" >&2
    exit 1
fi

# --- Print dmesg tail ---
code_output=$(sudo dmesg) # | tail -n "$dmesg_lines")
echo $code_output

# Extract PS Output Timestamp
ps_timestamp=$(echo "$ps_output" | grep -oE '[0-9]+:[0-9]+:[0-9]+')
# Extract Code output Timestamp
code_timestamp=$(echo "$code_output" | grep -oE '[0-9]+:[0-9]+:[0-9]+')

if [[ "$prod" -gt 0 && "$cons" -gt 0 ]]; then
    percent_diff_time "$ps_timestamp" "$code_timestamp"
fi


# --- End of script ---
exit 0
