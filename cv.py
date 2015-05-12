import os
import cv2
import numpy as np
import sys
#from matplotlib import pyplot as plt
from datetime import datetime
import random
import logging
r = lambda: random.randint(0, 255)

logger = logging.getLogger("pi-coin-scanner.cv")


class SimplePlot:
  def __init__(self, shrink_factor=None):
    self.n = 1

  def __call__(self, img, name):
    plt.subplot(1,1, self.n)
    plt.imshow(img, 'gray')
    plt.title(name)
    plt.xticks([])
    plt.yticks([])
    self.n += 1


class IntermediateImageSaver:
  def __init__(self, prefix, dest, scale=None):
    self.n = 1
    self.prefix = prefix
    self.dest = dest
    self.scale = scale

    if not os.path.exists(dest):
      os.makedirs(dest)

  def __call__(self, img, name):
    if self.scale is not None:
      for i in range(self.scale):
        img = cv2.pyrUp(img)

    cv2.imwrite(
      os.path.join(
        self.dest,
        "{0}_{1}_{2}.png".format(self.prefix, self.n, name)
      ), img
    )
    self.n += 1


class ImageCropper:
  def __init__(self, original_file, dest):
    self.dest = dest
    self.filename = os.path.basename(original_file).split(".")[0]
    self.img = cv2.imread(original_file)
    self.n = 0

    if not os.path.exists(dest):
      os.makedirs(dest)

  def __call__(self, min_x, max_x, min_y, max_y):
    cropped_img = self.img[min_y:max_y, min_x:max_x]
    cropped_img_url = os.path.join(
      self.dest, "{0}_{1}.png".format(self.n, self.filename)
    )
    cv2.imwrite(cropped_img_url, cropped_img)
    self.n += 1
    return cropped_img_url


class CroppingBox:
  def __init__(self, x, y, w, h):
    self.x = x
    self.y = y
    self.w = w
    self.h = h
    self.centroid = (x + (w/2), y + (h/2))

  def area(self):
    return self.w * self.h

  def expand(self, border):
    box = CroppingBox(
      x=self.x+border,
      y=self.y+border,
      w=self.w,
      h=self.h,
    )
    logger.debug("Expanding borders of {0} by {1} pixels".format(self, border))
    return box

  def getCorners(self):
    return {
      "min_x": self.x,
      "max_x": self.x+self.w,
      "min_y": self.y,
      "max_y": self.y+self.h,
    }

  def __str__(self):
    return "<CroppingBox(area={0}, w={1}, h={2}, upper_left={3}, lower_right={4})>".format(
      self.area(),
      self.w,
      self.h,
      (self.x, self.y),
      (self.x+self.w, self.y+self.h),
    )


class ImageFromScan:
  def __init__(self, box, img):
    self.url = img
    self.box = box
    self.h = box.h
    self.w = box.w


class SplitScan:
  def __init__(self):
    self.split_imgs  = []

  def add(self, box, img):
    self.split_imgs.append(ImageFromScan(box=box, img=img))

  def __iter__(self):
    for i in self.split_imgs:
      yield i

  def __len__(self):
    return len(self.split_imgs)


def img2bounding_box(url, intermediate_destination, cropped_destination, border_reduction):
  assert os.path.exists(url), "There exists no file {0}".format(url)

  start = datetime.now()


  archiver = IntermediateImageSaver(
    prefix=os.path.basename(url).split(".")[0],
    dest=intermediate_destination,
  )
  cropper = ImageCropper(url, dest=cropped_destination)
  split = SplitScan()

  img = cv2.imread(url)

  reduced_border_img = img[
    border_reduction:-border_reduction,
    border_reduction:-border_reduction
  ]
  #for i in range(scale_exponent):
  #  reduced_border_img = cv2.pyrDown(reduced_border_img)

  gray_img = cv2.cvtColor(reduced_border_img, cv2.COLOR_BGR2GRAY)
  archiver(gray_img, "gray")

  threshold = cv2.adaptiveThreshold(
    gray_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
  )
  archiver(threshold, "threshold")

  kernel = np.ones((8, 8),np.uint8)
  opening = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)
  archiver(opening, "opening")

  closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
  archiver(closing, "closing")

  negated = cv2.bitwise_not(closing)
  archiver(negated, "negated")

  contours, hierarchy = cv2.findContours(
    negated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
  )
  blank_image_contours = np.zeros(img.shape, np.uint8)
  blank_image = np.zeros(img.shape, np.uint8)

  next_countour_indices = hierarchy[0,:,0]
  next_index = 0
  while next_index != -1:
    c = contours[next_index]
    cv2.drawContours(blank_image_contours, c, -1, (255, 0, 0), 5)
    x,y,w,h = cv2.boundingRect(c)
    box = CroppingBox(x=x, y=y, w=w, h=h)
    
    # scale up these coordinates to their original size
    if box.area() > 22179:
      box = box.expand(border_reduction)
      logger.debug(box)

      img = cropper(**box.getCorners())
      split.add(box=box, img=img)

      lx = box.x
      ly = box.y
      rx = lx+box.w
      ry = ly+box.h
      cv2.rectangle(blank_image, (lx, ly), (rx, ry), (r(), r(), r()), 10)

    next_index = next_countour_indices[next_index]

  logger.info("Number of detected objects: {0}".format(len(split)))
  archiver(blank_image_contours, "contours")
  archiver(blank_image, "bounding_boxes")

  duration = datetime.now() - start
  logger.info("Splitting time: {0}".format(duration))

  return split


if __name__ == "__main__":
  INTERMEDIATE_IMAGE_DIRECTORY = "intermediate"
  CROPPED_IMAGE_DIRECTORY = "cropped"
  testing_samples = {
    "sample/white_background.tiff": 6,
    "sample/001.tiff": 8,
    "sample/002.tiff": 1,
    "sample/003.tiff": 1,
    "sample/2015-05-08_1.tiff": 5,
    "sample/2015-05-08_2.tiff": 5,
  }

  border_reduction = 50
  for url in testing_samples:
    boxes = img2bounding_box(
      url=url,
      intermediate_destination=INTERMEDIATE_IMAGE_DIRECTORY,
      cropped_destination=CROPPED_IMAGE_DIRECTORY,
      border_reduction=border_reduction,
    )
    if len(boxes) != testing_samples[url]:
      logger.error(
        "For {0}, the expected number of bounding boxes ({1}) did not equal"
        " the actual number ({2})".format(
          os.path.basename(url), testing_samples[url], len(boxes)
      ))

