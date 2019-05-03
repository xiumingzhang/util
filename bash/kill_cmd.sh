#!/usr/bin/env bash

if [ "$#" -ne 1 ]; then
    echo "Exactly one argument required!"
    echo "    1. Start of the commands to kill (e.g., 'python very_heavy_job.py')"
    exit 1
fi

user=$(whoami)

# CPU
for id in {1..38}; do
    printf -v m "vision%02d" "$id"
    ssh "$user@$m.csail.mit.edu" "pkill -9 -f \"$1\"" &
    echo "$1: killed on $m"
done

# GPU
for id in {2..43}; do
    printf -v m "visiongpu%02d" "$id"
    ssh "$user@$m.csail.mit.edu" "pkill -9 -f \"$1\"" &
    echo "$1: killed on $m"
done
