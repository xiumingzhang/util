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

# Figure out input frame height
frame_f=$(find $regex | head -1)
wxh=$(file ${frame_f} | cut -d',' -f2) # get image dimensions
h=$(echo ${wxh} | awk -F' x ' '{print $2}')

ffmpeg -framerate "$fps" -pattern_type glob -i "$regex" -vf scale=-2:"$h" -pix_fmt yuv420p "$outpath" -y

# To preserve alpha channel
#ffmpeg -framerate "$fps" -pattern_type glob -i "$regex" -vf scale=-2:720 -vcodec png "$outpath" -y

echo 'Successful!'
echo -e "All images matching $regex are compiled into $outpath"
