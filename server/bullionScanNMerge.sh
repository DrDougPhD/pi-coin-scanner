# Doug McGeehan (djmvfb@mst.edu)
#
# This script expects raw scanned images to be named in the following format:
#   ${prefix}_f.tiff for obverse scans, and
#   ${prefix}_b.tiff for reverse scans.
# We need both of these files to perform the final merging. When you perform
#   the scan, make sure to keep the ingots in approximately the same location
#   on the scanner.
#
# First, you need multicrop. Download it from here:
#  http://www.fmwconcepts.com/imagemagick/multicrop/index.php
# Make this script executable: sudo chmod multicrop +x
#

# Create a temporary directory for intermediate files
TMP_DIR="/tmp/bullion"
[ -d ${TMP_DIR} ] || mkdir ${TMP_DIR}

# multicrop will split the raw scan based on the unique regions of the raw
#   image, where each region corresponds to one ingot. The output files will be
#   of the format:
#     ${prefix}_f-NUM.tiff and ${prefix}_b-NUM.tiff

for f in "${1}"/*.tiff
do
  echo "Splitting ingots from $f"
 
  # -u 3 does not perform unrotate. These are scans of ingots.
  #    They do not need to be rotated.
  # -f 25 is a fuzzy-comparison value to determine if a color is
  #    approximately equal to the background color provided in the
  #    south-west corner of the image. Since ingots are thicker than
  #    photographs, they will cast a shadow in the scan, and this fuzziness
  #    is needed to separate the many ingots in the scan.
  img_filename=`basename "$f"`
  time ./multicrop -c West -u 3 -f 15 "$f" "${TMP_DIR}/${img_filename}"
  echo "--------------------------------------------------------------------"
done

# I am assuming that multicrop will split the two scans in the same order
#   so that for some prefix and NUM, ${prefix}_f-NUM.tiff and 
#   ${prefix}_b-NUM.tiff will correspond to the obverse and reverse of the
#   same ingot.
#     e.g. 2014.12.03_f-001.tiff and 2014.12.03_b-001.tiff should be
#       the obverse and reverse of the same ingot.
# To allow two corresponding images to be merged together, observe that the
#   difference in filenames for the obverse and reverse of the same ingot
#   is the character "f" or "b".
#     e.g. 2014.12.03_f-001.tiff and 2014.12.03_b-001.tiff correspond to the
#       same ingot
#   Thus, if we wildcard this character, then we'll have both the filename of
#   the obverse and the reverse for the same corresponding bar/round.
#     e.g. 2014.12.03*-001.tiff resolves to 2014.12.03_b-001.tiff and 
#       2014.12.03_f-001.tiff
ls ${TMP_DIR}/*.tiff |
  sed -rn 's/(.+_)[[:digit:]]+(-[[:digit:]]+\.tiff)/\1*\2/p' |
  sort | uniq -d | while read img; do
  # imgmerge.sh is actually receiving two parameters because of the above-
  #   mentioned wildcard. Parameters 1 and 2 are the result of expanding the
  #   wildcard, and thus are in lexicographic order.
  #     e.g. 2014.12.03_b-001.tiff comes before 2014.12.03_f-001.tiff in
  #       lexicographic order.
  #   Thus, the obverse image (_f) will occur after the reverse image (_b).
  #   Since the images should be merged so that the obverse image is on the 
  #   top/left, the script imgmerge was written to expect the reverse image as
  #   the first parameter, and the obverse image as the second parameter.
  time bash imgmerge.sh ${img} "$1"
  echo "--------------------------------------------------------------------"
done

# Clean up intermediate files
echo "Cleaning up intermediate files in ${TMP_DIR}"
rm -R ${TMP_DIR}

