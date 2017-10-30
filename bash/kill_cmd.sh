#!/usr/bin/env bash

if [ "$#" -ne 1 ]; then
    echo "Exactly one argument required!"
    echo "    1. Start of the commands to kill (e.g., 'python very_heavy_job.py')"
    exit 1
fi

cpu_list=( 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 )
gpu_list=( 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 18 19 20 )

user=$(whoami)

# CPU
for id in "${cpu_list[@]}"; do
    printf -v m "vision%02d" "$id"
    ssh "$user@$m.csail.mit.edu" "pkill -9 -f \"$1\"" &
    echo "$1: killed on $m"
done

# GPU
for id in "${gpu_list[@]}"; do
    printf -v m "visiongpu%02d" "$id"
    ssh "$user@$m.csail.mit.edu" "pkill -9 -f \"$1\"" &
    echo "$1: killed on $m"
done
