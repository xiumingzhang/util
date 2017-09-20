#!/usr/bin/env bash

if [ "$#" -ne 3 ]; then
    echo "Exactly three arguments required!"
    echo "    1. Single-quoted regex (e.g., './*.png', '/data/results/???.png', etc.)"
    echo "    2. Frame rate"
    echo "    3. Output path"
    exit 1
fi
regex=$1
fps=$2
outpath=$3

ffmpeg -framerate "$fps" -pattern_type glob -i "$regex" -vf scale=-2:720 -pix_fmt yuv420p "$outpath"

echo 'Successful!'
echo -e "All images matching $regex are compiled into $outpath"
