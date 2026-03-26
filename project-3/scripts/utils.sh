#!/bin/bash

# This is the username of the user we will create and use to test
USERNAME="TestP3"

# Kernel module correctness
KERNEL_MODULE_NAME="producer_consumer"
KERNEL_MODULE_ERR=""
HOME_DIR="/home/${USERNAME}"

load_module_with_params() {
    local prod=$1
    local cons=$2
    local size=$3
    local uid=$4

    if [ ! -e "${KERNEL_MODULE_NAME}.ko" ]; then
        KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - Failed to find kernel object ${KERNEL_MODULE_NAME}.ko"
        return 1
    fi

    sudo dmesg -c >/dev/null 2>/dev/null

    local insmod_err
    insmod_err=$(sudo insmod "${KERNEL_MODULE_NAME}.ko" prod="$prod" cons="$cons" size="$size" uid="$uid" 2>&1)
    if [ $? -ne 0 ]; then
        KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - Insmod exited with non-zero return code => ${insmod_err}"
        return 1
    fi

    if ! sudo lsmod | grep -q "^${KERNEL_MODULE_NAME}\b"; then
        KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - Kernel module does not appear in lsmod"
        return 1
    fi

    return 0
}

check_threads() {
    local prod=$1
    local cons=$2
    local points=$3
    local count

    count=$(ps -e -o comm= | grep -Eci '^k?Producer-')
    if [ "$count" -ne "$prod" ]; then
        KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - Found ${count} producer threads, expected ${prod} (-${points} points)"
        return 1
    fi

    count=$(ps -e -o comm= | grep -Eci '^k?Consumer-')
    if [ "$count" -ne "$cons" ]; then
        KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - Found ${count} consumer threads, expected ${cons} (-${points} points)"
        return 1
    fi

    return 0
}

start_processes() {
    local regular=$1
    local zombies=$2
    local i

    i=0
    while [ "$i" -lt "$regular" ]; do
        sudo su -s /bin/bash "$USERNAME" -c "${HOME_DIR}/process_generator regular" > /dev/null 2>&1 &
        i=$((i + 1))
        sleep 0.02
    done

    i=0
    while [ "$i" -lt "$zombies" ]; do
        sudo su -s /bin/bash "$USERNAME" -c "${HOME_DIR}/process_generator zombie" > /dev/null 2>&1 &
        i=$((i + 1))
        sleep 0.02
    done
}

compare_pids() {
    local prod=$1
    local cons=$2
    local regular=$3
    local zombies=$4
    local base_regular="$5"
    local zombie_pids="$6"

    local regular_pids_alive
    local zombie_pids_alive
    local zombie_pids_alive_len

    regular_pids_alive=$(ps -u "$USERNAME" -o pid=,args= | awk '/process_generator regular/ {print $1}' | sort)
    zombie_pids_alive=$(ps -u "$USERNAME" -o pid=,args= | awk '/process_generator zombie/ {print $1}' | sort)

    zombie_pids_alive_len=$(echo "$zombie_pids_alive" | wc -w)
    if [ "$zombie_pids_alive_len" -ne 0 ]; then
        KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - Found ${zombie_pids_alive_len} zombie processes still alive, expected 0. PIDs: ${zombie_pids_alive}"
        return 1
    fi

    if [ "$base_regular" != "$regular_pids_alive" ]; then
        KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - Regular processes changed unexpectedly. Expected alive PIDs: ${base_regular}. Found alive PIDs: ${regular_pids_alive}"
        return 1
    fi

    return 0
}

unload_module() {
    sudo dmesg -c >/dev/null 2>/dev/null

    local rmmod_out
    rmmod_out=$(timeout 15s sudo rmmod "${KERNEL_MODULE_NAME}" 2>&1)

    if sudo lsmod | grep -q "^${KERNEL_MODULE_NAME}\b"; then
        KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - Failed to unload kernel module. Error: ${rmmod_out}"
        return 1
    fi

    return 0
}