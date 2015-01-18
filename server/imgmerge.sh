# Doug McGeehan (djmvfb@mst.edu)
#
# This script expects to receive two parameters corresponding to the obverse
#   and reverse of the same ingot. The first parameter should be the path
#   to the reverse image, and the second parameter should be the path to the
#   obverse image.
#   e.g. ${1} == 2014.12.03_0-001.tiff
#        ${2} == 2014.12.03_1-001.tiff
# The expected output, given 2014.12.03_0-001.tiff and 2014.12.03_1-001.tiff
#   as arguments, is a merged image 2014.12.03-001.jpg. Merging is either
#   horizontal or vertical based on the aspect ratios of the images. Generally
#   all rounds are horizontally merged. Portrait-oriented bars are horizontally
#   merged. Landscape-oriented bars are vertically merged.
#   If the images are merged horizontally, then 2014.12.03_0-001.tiff will
#   be to the left of 2014.12.03_1-001.tiff in the merged image.
#   If the images are merged vertically, then 2014.12.03_0-001.tiff will
#   be above 2014.12.03_1-001.tiff in the merged image.
echo "Merging ${1} and ${2}..."

# Convert the filename 2014-12-03_b-005.tiff to 2014-12-03-005.jpg
img="${3}/$(basename ${1} | sed -rn 's|(.*)_[[:digit:]]+(-.*)\.tiff|\1\2.jpg|p')"

# If the aspect ratio of one of the images is less than 1, with some wiggle 
#  room, then the two files will be vertically merged. Otherwise, horizontal
#  merging.
h=$(identify -format "%h" "${1}")
w=$(identify -format "%w" "${1}")
if (( $(bc <<< "scale=2; $h/$w < 0.95") == 1 ))

# Image 1 and 2 are the result of expanding a wildcard, and thus are in
#  lexicographic order.
#    e.g. 2014.12.03_0-001.tiff comes before 2014.12.03_1-001.tiff in
#      lexicographic order.
#  Thus, the obverse image (_f) will occur after the reverse image (_b).
#  Since the images should be merged so that the obverse image is on the 
#  top/left, I'm rearranging the 1st and 2nd argument to deal with this
#  issue.
then
    # Vertical merging
    echo "Vertical merging of ${1} and ${2} => ${img}"
    convert "${1}" "${2}" -append "${img}"
else
    # Horizontal merging
    echo "Horizontal merging ${1} and ${2} => ${img}"
    convert "${1}" "${2}" +append "${img}"
fi
