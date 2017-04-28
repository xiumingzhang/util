#! /bin/bash

if [ "$#" -ne 2 ]; then
    echo "Exactly two arguments required!"
    echo "    1. Machine numeric ID (e.g., 1, 10)"
    echo "    2. Boolean for whether it is a GPU machine (0 or 1)"
    exit 1
fi

TIMEOUT=10s

ID=${1}
isGPU=${2}
user=`whoami`

if [[ ${isGPU} == 1 ]]; then
    printf -v i "gpu%02d" ${ID}
elif [[ ${isGPU} == 0  ]]; then
    printf -v i "%02d" ${ID}
else
    echo "The second argument must be either 0 or 1"
    exit 1
fi

timeout ${TIMEOUT} ssh -q ${user}@vision${i}.csail.mit.edu exit
if [ $? -eq 124 ]; then
    echo dead
else
    echo alive
fi
