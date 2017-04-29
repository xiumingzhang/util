#! /bin/bash

if [ "$#" -ne 2 ]; then
    echo "Exactly two arguments required!"
    echo "    1. List of machines on which jobs are NOT to be killed (e.g., '4 14')"
    echo "    2. List of booleans for whether they are GPU machines (e.g., '1 0')"
    exit 1
fi

CPUList=( 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 )
GPUList=( 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 )

dontKillIDs=${1}
dontKillIDs=(${dontKillIDs// / })
isGPUs=${2}
isGPUs=(${isGPUs// / })

user=`whoami`

# CPU
for ID in ${CPUList[@]}; do
    toKill=1
    # Check if it's in no-kill list
    for i in ${!isGPUs[@]}; do
        if [[ ${isGPUs[i]} == 0 ]]; then # is a CPU
            if [[ ${dontKillIDs[i]} == ${ID} ]]; then
                toKill=0
            fi
        fi
    done
    # Kill
    if [[ ${toKill} == 1 ]]; then
        printf -v ID "%02d" ${ID}
        ssh ${user}@vision${ID}.csail.mit.edu "pkill -9 -u ${user}"
    fi
done

# GPU
for ID in ${GPUList[@]}; do
    toKill=1
    # Check if it's in no-kill list
    for i in ${!isGPUs[@]}; do
        if [[ ${isGPUs[i]} == 1 ]]; then # is a GPU
            if [[ ${dontKillIDs[i]} == ${ID} ]]; then
                toKill=0
            fi
        fi
    done
    # Kill
    if [[ ${toKill} == 1 ]]; then
        printf -v ID "gpu%02d" ${ID}
        ssh ${user}@vision${ID}.csail.mit.edu "pkill -9 -u ${user}"
    fi
done
