#!/usr/bin/env bash

if [ "$#" -ne 6 ]; then
    echo "Exactly six arguments required!"
    echo "    1. Single-quoted regex for image filename patterns (e.g., './*', '/results/???', etc.)"
	echo "    2. Suffix for left/top images (e.g., _orig.png)"
	echo "    3. Suffix for right/bottom images (e.g., _recon.png)"
    echo "    4. Frame rate"
	echo "    5. Stacking direction (h or v)"
    echo "    6. Output path"
    exit 1
fi
prefix_regex=$1
lsuffix=$2
rsuffix=$3
fps=$4
stackdir=$5
outpath=$6

tmp_outdir=/var/tmp
suffix_for_id=_stacked.png
rm -rf "${tmp_outdir:?}"/*"$suffix_for_id"

for lf in $prefix_regex$lsuffix; do
	rf="${lf//$lsuffix/$rsuffix}"

	xbase="${lf##*/}"
	prefix="${xbase%$lsuffix}"
	tmp_outpath="$tmp_outdir/${prefix}_stacked.png"

	# Get image dimensions
	wxh=$(file "$rf" | cut -d',' -f2)
	rw=$(echo "$wxh" | awk -F' x ' '{print $1}')
	rh=$(echo "$wxh" | awk -F' x ' '{print $2}')

	# Stack pairs of images
	if [[ "$stackdir" == h ]]; then
		ffmpeg -i "$lf" -i "$rf" -filter_complex "[1][0]scale2ref=ih*($rw/$rh):ih[2nd][ref];[ref][2nd]hstack" "$tmp_outpath"
	else
		ffmpeg -i "$lf" -i "$rf" -filter_complex "[1][0]scale2ref=iw:iw*($rh/$rw)[2nd][ref];[ref][2nd]vstack" "$tmp_outpath"
	fi
done

ffmpeg -framerate "$fps" -pattern_type glob -i "$tmp_outdir/*_stacked.png" -vf scale=-2:720 -pix_fmt yuv420p "$outpath"

echo 'Successful!'
echo -e "See $outpath for the result"
