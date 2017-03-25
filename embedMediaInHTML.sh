#! /bin/bash

#if [ "$#" -ne 1 ]; then
#    echo "Exactly one argument (width) required!"
#    exit 1
#fi
#width=$1
width=250

nPerRow=8

exts=( "png" "jpg" "mp4" )
htmlF="all.html"

array_contains2 () { 
    local array="$1[@]"
    local seeking=$2
    local in=1
    for element in "${!array}"; do
        if [[ $element == $seeking ]]; then
            in=0
            break
        fi
    done
    return $in
}

rm -f "${htmlF}"
echo -e "<!DOCTYPE HTML>\n<html>\n<body>\n<center>\n<table border=1>" >> "${htmlF}"
# For every file
i=0
for f in ./*; do
    xbase="${f##*/}"
    xfext="${xbase##*.}"
    # If media file
    if array_contains2 exts "${xfext}"; then
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
    fi
done
echo -e "\n</table>\n</center>\n</body>\n</html>" >> "${htmlF}"
echo -e "All media files embedded into ./${htmlF}!"
