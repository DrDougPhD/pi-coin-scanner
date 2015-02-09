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
  def __init__(self):
    self.n = 1

  def __call__(self, img, name):
    plt.subplot(1,1, self.n)
    plt.imshow(img, 'gray')
    plt.title(name)
    plt.xticks([])
    plt.yticks([])
    self.n += 1


class IntermediateImageSaver:
  def __init__(self, prefix):
    self.n = 1
    self.prefix = prefix

  def __call__(self, img, name):
    cv2.imwrite(
      "output/{0}_{1}_{2}.png".format(self.prefix, self.n, name),
      img
    )
    self.n += 1


def img2bounding_box(url, border_reduction):
  archiver = IntermediateImageSaver(
    prefix=os.path.basename(url).split(".")[0]
  )

  img = cv2.imread(url)[
    border_reduction:-border_reduction,
    border_reduction:-border_reduction
  ]
  gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  archiver(gray_img, "gray")

  blur = cv2.GaussianBlur(gray_img, (5, 5), 0)
  archiver(blur, "blur")

  _, threshold = cv2.threshold(
    blur, 0, 255,
    cv2.THRESH_BINARY+cv2.THRESH_OTSU
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
    x,y,w,h = cv2.boundingRect(c)
    bounding_boxes.append((x,y,w,h))

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
    assert len(boxes) == testing_samples[url], (
      "For {0}, the expected number of bounding boxes ({1}) did not equal"
      " the actual number ({1})".format(
        os.path.basename(url) ,testing_samples[url], len(boxes)
    ))
