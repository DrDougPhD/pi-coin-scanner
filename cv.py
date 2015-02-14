import os
import cv2
import numpy as np
import sys
from matplotlib import pyplot as plt
import random
r = lambda: random.randint(0,255)

"""
# global thresholding
ret1,th1 = cv2.threshold(img,127,255,cv2.THRESH_BINARY)

# Otsu's thresholding
ret2,th2 = cv2.threshold(img,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
"""

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
  def __init__(self, prefix, scale=None):
    self.n = 1
    self.prefix = prefix
    self.scale = scale

  def __call__(self, img, name):
    if self.scale is not None:
      for i in range(self.scale):
        img = cv2.pyrUp(img)

    cv2.imwrite(
      "output/{0}_{1}_{2}.png".format(self.prefix, self.n, name),
      img
    )
    self.n += 1


class ImageCropper:
  def __init__(self, img, original_file):
    self.filename = os.path.basename(original_file).split(".")[0]
    self.img = cv2.imread(original_file)
    self.n = 0

  def __call__(self, min_x, max_x, min_y, max_y):
    cropped_img = self.img[min_y:max_y, min_x:max_x]
    cv2.imwrite("cropped/{0}_{1}.png".format(self.n, self.filename), cropped_img)
    self.n += 1


def img2bounding_box(url, border_reduction):
  scale_exponent = 4
  archiver = IntermediateImageSaver(
    prefix=os.path.basename(url).split(".")[0]
  )
  cropper = ImageCropper(url)

  img = cv2.imread(url)

  reduced_border_img = img[
    border_reduction:-border_reduction,
    border_reduction:-border_reduction
  ]
  for i in range(scale_exponent):
    reduced_border_img = cv2.pyrDown(reduced_border_img)

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
  i = 0
  bounding_boxes = []
  while next_index != -1:
    i += 1
    c = contours[next_index]
    cv2.drawContours(blank_image_contours, c, -1, (255, 0, 0), 5)
    rect = cv2.boundingRect(c)
    x,y,w,h = rect
    
    # scale up these coordinates to their original size
    min_x = (x*2**scale_exponent) + border_reduction
    min_y = (y*2**scale_exponent) + border_reduction
    max_x = min_x + (w*2**scale_exponent)
    max_y = min_y + (h*2**scale_exponent)
    cropper(min_x=min_x, max_x=max_x, min_y=min_y, max_y=max_y)

    bounding_boxes.append((min_x, max_x, min_y, max_y))

    print("Size: {0}  | ".format(w*h), (x,y), (x+w, y+h), (w, h))
    cv2.rectangle(blank_image, (x,y), (x+w,y+h), (r(), r(), r()), 10)
    next_index = next_countour_indices[next_index]

  print("Number of detected objects: {0}".format(i))
  archiver(blank_image_contours, "contours")
  archiver(blank_image, "bounding_boxes")

  return bounding_boxes


if __name__ == "__main__":
  testing_samples = {
    "sample/white_background.tiff": 6,
    "sample/001.tiff": 8,
    "sample/002.tiff": 1,
    "sample/003.tiff": 1,
  }

  border_reduction = 50
  for url in testing_samples:
    boxes = img2bounding_box(url=url, border_reduction=border_reduction)
    if len(boxes) != testing_samples[url]:
      print(
        "For {0}, the expected number of bounding boxes ({1}) did not equal"
        " the actual number ({2})".format(
          os.path.basename(url), testing_samples[url], len(boxes)
      ))

    
