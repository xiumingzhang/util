#!/usr/bin/env bash

user=$(whoami)
currdir=$(pwd)

n_per_session=100
machine_list=( 4 5 6 8 9 12 15 21 22 23 24 25 27 28 30 35 36 37 38 g2 g3 g4 g5 g6 g7 g8 g9 g10 g11 g12 g13 g14 g15 g16 g17 g18 g19 g20 )

n_machines=${#machine_list[@]}

cmd0="cd $currdir"

i=0
for cat_dir in ./jobs/*; do
    for obj_jobs in $cat_dir/*.m; do
        xbase=${obj_jobs##*/}

        if (( $((i%n_per_session)) == 0 )); then
            cmd="matlab -r \"addpath('$cat_dir'); "
        fi

        cmd="$cmd${xbase%.m}; "

        if (( $((i%n_per_session)) == n_per_session-1 )); then
            cmd="${cmd}exit;\""

            id="${machine_list[$((RANDOM%n_machines))]}"
            if [[ ${id:0:1} == g ]]; then
                # GPU machine
                printf -v id "gpu%02d" "${id:1:${#id[@]}+1}"
            else
                # CPU machine
                printf -v id "%02d" "$id"
            fi
            ssh "$user@vision$id.csail.mit.edu" "$cmd0; $cmd; exit" &
            echo "$obj_jobs submitted to vision$id"
        fi

        i=$((i+1))
    done
done
