#! /bin/bash

if [ "$#" -ne 2 ]; then
    echo "Exactly two arguments required!"
    echo "    1. Single-quoted regex (e.g., '*.png', '???.png', etc.)"
    echo "    2. Frame rate"
    exit 1
fi
regex=$1
fps=$2

ffmpeg -framerate ${fps} -pattern_type glob -i "${regex}" -vf scale=-2:720 -pix_fmt yuv420p video.mp4

echo "Successful!"
echo -e "All images matching ${regex} are compiled into `pwd`/video.mp4"
