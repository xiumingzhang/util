#! /bin/bash

if [ "$#" -ne 3 ]; then
    echo "Exactly three arguments required!"
    echo "    1. Single-quoted regex (e.g., '*.mp4', '*_azimuth0.png')"
    echo "    2. Media width (in pixels)"
    echo "    3. Number of media per row"
    exit 1
fi
regex=$1
width=$2
nPerRow=$3

htmlF="results.html"

rm -f "${htmlF}"
echo -e "<!DOCTYPE HTML>\n<html>\n<body>\n<center>\n<table border=1>" >> "${htmlF}"
# For every file
i=0
for f in ./${regex}; do
    xbase="${f##*/}"
    xfext="${xbase##*.}"
    # A new row
    if (( i == 0 )); then
        echo -e "\t<tr>" >> "${htmlF}"
    fi
    # If video
    if [[ "${xfext}" == "mp4" ]]; then
        echo -e "\t\t<td align=center>${xbase}\n<br><video width=\"${width}\" autoplay loop><source src=\"${f}\" type=\"video/mp4\"></video></td>" >> "${htmlF}"
    else # image
        echo -e "\t\t<td align=center>${xbase}\n<br><img src=\"${f}\" width=${width}></td>" >> "${htmlF}"
    fi
    # End of this row
    if (( i == nPerRow - 1 )); then
        echo -e "\t</tr>" >> "${htmlF}"
    fi
    i=$((i+1))
    i=$((i%nPerRow))
done
echo -e "\n</table>\n</center>\n</body>\n</html>" >> "${htmlF}"

echo "Successful!"
echo -e "All files matching ${regex} are embedded into `pwd`/${htmlF}!"
