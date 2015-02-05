import sys
from PIL import Image
from itertools import zip_longest

url = sys.argv[1]
img = Image.open(url)
print(img.format, img.size, img.mode)
lumoscity = img.convert("L")
concatenated_histogram = img.histogram()

def grouper(iterable, n, fillvalue=None):
  "Collect data into fixed-length chunks or blocks"
  # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
  args = [iter(iterable)] * n
  return zip_longest(fillvalue=fillvalue, *args)

num_colors_per_band = len(concatenated_histogram)//3
R, G, B = grouper(concatenated_histogram, num_colors_per_band)
histogram = [r+g+b for r, g, b in zip(R, G, B)]
#histogram = concatenated_histogram

print("+"*80)
with open("{0}.csv".format(url), 'w') as f:
  f.write("\n".join([str(h) for h in histogram]))

def peak1d(A, start, end):
  midpoint = (start+end)//2
  is_peak = (A[midpoint-1] <= A[midpoint] >= A[midpoint+1])
  if is_peak:
    return midpoint

  #########################################################  
  # The code will only come here if:
  #  1. m-1 falls to m; or
  #  2. m rises to m+1
  #########################################################
  #
  # If m-1 falls to m, then the peak is before the midpoint
  is_falling = (A[midpoint-1] > A[midpoint])
  if is_falling:
    return peak1d(A, start, midpoint-1)
  
  # If m rises to m+1, then the peak is after the midpoint
  #   is_rising  = (A[midpoint] < A[midpoint+1])
  #   if is_rising:
  return peak1d(A, midpoint+1, end)


###############################################################################
# The histogram of the scanned image has two "peaks". One slow slope in the
#   first half and one sharp slope in the second half.
#   Let's find the peak of the first half.
n = len(histogram)
m = n//2
slow_peak_location = peak1d(histogram, 0, m)
slow_peak = histogram[slow_peak_location]
print("Slow peak found at {0} with color value {1}".format(
  slow_peak_location, slow_peak
))

###########################################################
# Now find the first location in the second half that has
#  this peak value. This will be the threshold value.
threshold = 0
for i in range(m+1, n):
  if histogram[i] >= slow_peak:
    threshold = i
    break

print("Color removal will occur for pixels less than {0}".format(threshold))
masked = img.point(lambda p: p < threshold and 255)
masked.show()
