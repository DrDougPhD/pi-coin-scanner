import logging
import os
import sys
from cv import img2bounding_box
from PIL import Image
from datetime import datetime

import logging
logger = logging.getLogger("pi-coin-scanner")

WHITE = (255, 255, 255)


class Merger:
  def __init__(self, dest):
    self.n = 0
    self.results = []
    self.dest = dest

    if not os.path.exists(dest):
      os.makedirs(dest)

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
      self.dest, "{0}_{1}.jpg".format(url_safe_datetime, self.n)
    )
    self.n += 1
    result.save(merged_url)

    self.results.append(merged_url)
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


def splitAndMerge(obverse, reverse, destination):
  merge = Merger(destination)

  obverse.reorderByMinimumDistance(reverse)

  for ingot1, ingot2 in zip(obverse, reverse):
    start = datetime.now()
    merged = merge(ingot1, ingot2)
    duration = datetime.now() - start
    print("#"*80)
    logger.info("{0} and {1} => {2}".format(ingot1.url, ingot2.url, merged))
    logger.info("Merging time: {0}".format(duration))
    print("#"*80)

  if len(obverse) != len(reverse):
    logger.error(
      "For the two scans, the number of split images is not equal "
      "({0} vs {1})".format(
        len(obverse), len(reverse)
    ))

  return merge.results


if __name__ == "__main__":
  MERGED_OUTPUT_DIRECTORY = "merged"
  INTERMEDIATE_IMAGE_DIRECTORY = "intermediate"
  CROPPED_IMAGE_DIRECTORY = "cropped"
  border_reduction = 50

  logging.basicConfig(
    level=logging.DEBUG,
    filename='/tmp/pi-scanner_{0}.log'.format(datetime.now().date()),
    filemode='w'
  )
  stdout = logging.StreamHandler()
  stdout.setLevel(logging.DEBUG)
  logger.addHandler(stdout)

  if len(sys.argv) < 3:
    testing_samples = [
      ("sample/2015-05-12_4.tiff", "sample/2015-05-12_5.tiff"),
      #("sample/002.tiff", "sample/003.tiff"),
      #("sample/2015-05-08_1.tiff", "sample/2015-05-08_2.tiff")
    ]
  else:
    testing_samples = [
      sys.argv[1:]
    ]


  for (url1, url2) in testing_samples:
    side1 = img2bounding_box(
      url=url1, border_reduction=border_reduction,
      intermediate_destination=INTERMEDIATE_IMAGE_DIRECTORY,
      cropped_destination=CROPPED_IMAGE_DIRECTORY,
    )
    side2 = img2bounding_box(
      url=url2, border_reduction=border_reduction,
      intermediate_destination=INTERMEDIATE_IMAGE_DIRECTORY,
      cropped_destination=CROPPED_IMAGE_DIRECTORY,
    )
    results = splitAndMerge(side1, side2, MERGED_OUTPUT_DIRECTORY)

