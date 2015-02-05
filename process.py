import sys
from PIL import Image
from itertools import zip_longest

def shrink(img, scale):
  w, h = img.size
  scaled_w = w//scale
  scaled_h = h//scale
  scaled_img = img.resize((scaled_w, scaled_h))
  return scaled_img


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



def create_mask(img):
  lumoscity = img.convert("L")
  histogram = lumoscity.histogram()

  print("+"*80)
  with open("{0}.csv".format(url), 'w') as f:
    f.write("\n".join([str(h) for h in histogram]))

############################################################
# The histogram of the scanned image has two "peaks". One 
#   slow slope in the first half and one sharp slope in the
#   second half. Let's find the peak of the first half.
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
  mask = lumoscity.point(lambda p: p < threshold and 255)
  return mask

if __name__ == "__main__":
  url = sys.argv[1]
  img = Image.open(url)
  print(img.format, img.size, img.mode)
  shrinked_img = shrink(img, 32)
  mask = create_mask(shrinked_img)
  expanded_mask = mask.resize(img.size)
  expanded_mask.show()
