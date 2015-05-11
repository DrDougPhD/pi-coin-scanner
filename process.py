import logging
import os
from cv import img2bounding_box
from PIL import Image
from datetime import datetime

import logging
logging.basicConfig(
  level=logging.DEBUG,
  filename='/tmp/pi-scanner_{0}.log'.format(datetime.now().date()),
  filemode='w'
)
logger = logging.getLogger("pi-coin-scanner")
stdout = logging.StreamHandler()
stdout.setLevel(logging.DEBUG)
logger.addHandler(stdout)


WHITE = (255, 255, 255)
MERGED_OUTPUT_DIRECTORY = "merged"


class Merger:
  def __init__(self):
    self.n = 0

  def __call__(self, img1, img2):
    # If the aspect ratio of one of the images is less than 1, with some wiggle 
    #  room, then the two files will be vertically merged. Otherwise, horizontal
    #  merging.
    if (img1.h / float(img1.w)) < 0.95:
      result = verticalMerge(img1, img2)

    else:
      result = horizontalMerge(img1, img2)

    url_safe_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    merged_url = os.path.join(
      MERGED_OUTPUT_DIRECTORY, "{0}_{1}.jpg".format(url_safe_datetime, self.n)
    )
    self.n += 1
    result.save(merged_url)
    return merged_url


def verticalMerge(img1, img2):
  logger.info("Vertical merging of {0} and {1}".format(img1.url, img2.url))
  max_width = max(img1.w, img2.w)
  concatenated_height = img1.h + img2.h
  result = Image.new("RGBA", (max_width, concatenated_height), color=WHITE)
  result.paste(Image.open(img1.url), (0, 0))
  result.paste(Image.open(img2.url), (0, img1.h))
  return result


def horizontalMerge(img1, img2):
  logger.info("Horizontal merging of {0} and {1}".format(img1.url, img2.url))
  max_height = max(img1.h, img2.h)
  concatenated_width = img1.w + img2.w
  result = Image.new("RGBA", (concatenated_width, max_height), color=WHITE)
  result.paste(Image.open(img1.url), (0, 0))
  result.paste(Image.open(img2.url), (img1.w, 0))
  return result


if __name__ == "__main__":
  testing_samples = [
    ("sample/002.tiff", "sample/003.tiff"),
    ("sample/2015-05-08_1.tiff", "sample/2015-05-08_2.tiff")
  ]

  border_reduction = 50
  if not os.path.exists(MERGED_OUTPUT_DIRECTORY):
    os.makedirs(MERGED_OUTPUT_DIRECTORY)

  for (url1, url2) in testing_samples:
    start = datetime.now()
    side1 = img2bounding_box(url=url1, border_reduction=border_reduction)
    duration = datetime.now() - start
    logger.info("Splitting time: {0}".format(duration))

    start = datetime.now()
    side2 = img2bounding_box(url=url2, border_reduction=border_reduction)
    duration = datetime.now() - start
    logger.info("Splitting time: {0}".format(duration))

    merge = Merger()

    for ingot1, ingot2 in zip(side1, side2):
      start = datetime.now()
      merged = merge(ingot1, ingot2)
      duration = datetime.now() - start
      print("#"*80)
      logger.info("{0} and {1} => {2}".format(ingot1.url, ingot2.url, merged))
      logger.info("Merging time: {0}".format(duration))
      print("#"*80)

    if len(side2) != len(side1):
      logger.error(
        "For the two scans, the number of split images is not equal "
        "({0} vs {1})".format(
          len(side1), len(side2)
      ))

