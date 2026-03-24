#!/bin/bash
source ./utils.sh

cleanup() {
    pkill -u "$USERNAME" -x process_generator >/dev/null 2>&1 || true

    if [ -n "$KERNEL_MODULE_ERR" ]; then
        echo -e "[log]: ─ Errors: ${KERNEL_MODULE_ERR}" >&2
    fi
}

trap cleanup EXIT

if [ $# -ne 6 ]; then
    echo "Error: Usage: $0 <submission_path> <num_producers> <num_consumers> <buffer_size> <regular> <zombie>" >&2
    exit 1
fi

path_to_build_script="$(cd "$(dirname "$0")" && pwd)"
path_to_kernel_module=$1
prod=$2
cons=$3
buffSize=$4
regular=$5
zombies=$6

zombies_pids=""

echo "[log]: Starting ${regular} normal processes"
start_processes "$regular" 0 &

cur_regular_count=0
while [ "$cur_regular_count" -ne "$regular" ]; do
    sleep 0.5
    base_regular=$(ps -u "$USERNAME" -o pid=,args= | awk '/process_generator regular/ {print $1}' | sort)
    cur_regular_count=$(echo "$base_regular" | wc -w)
done

if [ "$zombies" -ne 0 ]; then
    total_zombies=$zombies
    zombie_count=0

    if [ "$total_zombies" -le 100 ]; then
        batch_size=10
    else
        batch_size=100
    fi

    echo "[log]: Starting ${total_zombies} zombie processes ..."
    while [ "$zombie_count" -lt "$total_zombies" ]; do
        remaining=$((total_zombies - zombie_count))

        if [ "$remaining" -lt "$batch_size" ]; then
            current_batch_size=$remaining
        else
            current_batch_size=$batch_size
        fi

        start_processes 0 "$current_batch_size"
        zombie_count=$((zombie_count + current_batch_size))

        echo "[log]: ─ Total zombies spawned so far: $zombie_count/$total_zombies"
        sleep 1
    done
fi

uid=$(id -u "$USERNAME")
echo "[log]: Load the kernel module"
if ! load_module_with_params "$prod" "$cons" "$buffSize" "$uid"; then
    echo "[log]: ─ Failed to insert kernel module." >&2
    exit 1
else
    echo "[log]: ─ Kernel ModuleLoaded successfully"
fi

echo "[log]: ┬ We will wait 10 seconds"
sleep 10

echo "[log]: Checking the counts of the running kernel threads"
if ! check_threads "$prod" "$cons" 2; then
    echo "[log]: ─ Thread count check failed." >&2
else
    echo "[log]: ─ Found all expected threads"
fi

sleep 10

echo "[log]: Checking the pids of all remaining processes against your output"

if [ "$zombies" -ne 0 ] && [ -f "/home/$USERNAME/zombies.txt" ]; then
    zombies_pids=$(grep -Eo '[0-9]+' "/home/$USERNAME/zombies.txt" | sort -u)
fi

if ! compare_pids "$prod" "$cons" "$regular" "$zombies" "$base_regular" "$zombies_pids"; then
    echo "[log]: ─ PID check failed." >&2
else
    echo "[log]: All zombies were cleaned"
    echo "[log]: None of the regular processes were killed"
fi

echo "[log]: Unload the kernel module"
if ! unload_module; then
    echo "[log]: ─ Error: Failed to remove kernel module." >&2
else
    echo "[log]: ─ Kernel module unloaded successfully"
fi

echo "[log]: Checking to make sure kthreads are terminated"
if ! check_threads 0 0 3; then
    echo "[log]: ─ Failed to terminate all threads." >&2
else
    echo "[log]: ─ All threads have been stopped"
fi

exit 0