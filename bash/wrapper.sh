#!/usr/bin/env bash
python="${PY_DIR}/bin/python3.6"

user=$(whoami)
currdir=$(pwd)

clips=( ballet11-1 ballet11-2 djokovic1_cut jogging jogging2 jumping olympicRunning walking8_down4 walkingu wall )
textures=( tarp wood tiles transp marble leather cliff metal )
overwrite=0

cpu_list=( 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 24 25 26 28 29 30 31 32 33 34 35 36 37 38 )
n_machines=${#cpu_list[@]}

cmd0="cd ${currdir}"

i=0
# For every clip
for clip in "${clips[@]}"; do
    # For every texture
    for texture in "${textures[@]}"; do

		# Overwrite?
		outdir=/output/${clip}/${texture}
		if [[ ${overwrite} == 1 ]]; then
			rm -rf "${outdir}"
		fi

		# Define jobs
		cmd1="blender --background --python job.py -- ${clip} ${texture} ${outdir}"
		cmd2="${python} ${clip} ${texture} ${outdir}"

		# Probe machines
		idx=${i}
		while true; do
			id="${cpu_list[$((idx%n_machines))]}"
			printf -v id "%02d" "${id}"
			ssh -o ConnectTimeout=10 -o BatchMode=yes -o StrictHostKeyChecking=no -q \
				"${user}@vision${id}.csail.mit.edu" exit
			if [[ $? == 0 ]]; then
				break # found one machine alive
			else
				echo "vision${id} down"
			fi
			idx=$((idx+1)) # next machine
		done

		# Send jobs to the machine alive, if not done already
		if [[ ! -e ${outdir}/output1 ]] || [[ ! -e ${outdir}/output2 ]]; then
			ssh "${user}@vision${id}.csail.mit.edu" "${cmd0}; ${cmd1}; ${cmd2}; exit" &
			echo "${clip}, ${texture} submitted to vision${id}"
		else
			echo "${clip}, ${texture} done already, so not submitted to vision${ID}"
		fi

		i=$((i+1))
    done
done
