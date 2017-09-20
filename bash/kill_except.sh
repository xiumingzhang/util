#!/usr/bin/env bash

if [ "$#" -ne 2 ]; then
    echo "Exactly two arguments required!"
    echo "    1. List of machines on which jobs are NOT to be killed (e.g., '4 14')"
    echo "    2. List of booleans for whether they are GPU machines (e.g., '1 0')"
    exit 1
fi

cpu_list=( 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 )
gpu_list=( 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 18 19 20 )

dont_kill_ids=$1
dont_kill_ids=(${dont_kill_ids// / })
isgpu=$2
isgpu=(${isgpu// / })

user=$(whoami)

# CPU
for id in "${cpu_list[@]}"; do
    tokill=true
    # Check if it's in no-kill list
    for i in "${!isgpu[@]}"; do
        if [[ ${isgpu[i]} == 0 ]]; then # is a CPU
            if [[ ${dont_kill_ids[i]} == "$id" ]]; then
                tokill=false
            fi
        fi
    done
    # Kill
    if $tokill; then
        printf -v m "vision%02d" "$id"
        ssh "$user@$m.csail.mit.edu" "pkill -9 -u $user" &
        echo "Kill signal sent to $m"
    fi
done

# GPU
for id in "${gpu_list[@]}"; do
    tokill=true
    # Check if it's in no-kill list
    for i in "${!isgpu[@]}"; do
        if [[ ${isgpu[i]} == 1 ]]; then # is a GPU
            if [[ ${dont_kill_ids[i]} == "$id" ]]; then
                tokill=false
            fi
        fi
    done
    # Kill
    if $tokill; then
        printf -v m "visiongpu%02d" "$id"
        ssh "$user@$m.csail.mit.edu" "pkill -9 -u $user" &
        echo "Kill signal sent to $m"
    fi
done
