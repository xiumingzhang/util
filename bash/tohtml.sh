#!/usr/bin/env bash

if [ "$#" -ne 4 ]; then
    echo "Exactly four arguments required!"
    echo "    1. Single-quoted regex (e.g., '/data/results/*.mp4', './*_azimuth0.png')"
    echo "    2. Media width (in pixels)"
    echo "    3. Number of media per row"
	echo "    4. Output HTML path (e.g., '/data/results.html')"
    exit 1
fi
regex=$1
width=$2
n_per_row=$3
htmlf=$4

rm -f "$htmlf"
echo -e '<!DOCTYPE HTML>\n<html>\n<body>\n<center>\n<table border=1>' >> "$htmlf"

# For every file
i=0
for f in $regex; do
    xbase="${f##*/}"
    xfext="${xbase##*.}"

    # A new row
    if (( i == 0 )); then
        echo -e '\t<tr>' >> "$htmlf"
    fi
    # If video
    if [[ "$xfext" == mp4 ]]; then
        echo -e "\t\t<td align=center>${xbase}\n<br><video width=\"${width}\" autoplay loop><source src=\"${f}\" type=\"video/mp4\"></video></td>" >> "$htmlf"
    else # image
        echo -e "\t\t<td align=center>${xbase}\n<br><img src=\"${f}\" width=${width}></td>" >> "$htmlf"
    fi
    # End of this row
    if (( i == n_per_row - 1 )); then
        echo -e '\t</tr>' >> "$htmlf"
    fi
    i=$((i+1))
    i=$((i%n_per_row))
done
echo -e '\n</table>\n</center>\n</body>\n</html>' >> "$htmlf"

echo 'Successful!'
echo -e "All files matching $regex are embedded into $htmlf!"
