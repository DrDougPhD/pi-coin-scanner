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


if __name__ == "__main__":
  border_reduction = 50
  img = cv2.imread(sys.argv[1])[
    border_reduction:-border_reduction,
    border_reduction:-border_reduction
  ]
  gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  cv2.imwrite("01_gray.png", gray_img)

  blur = cv2.GaussianBlur(gray_img, (5, 5), 0)
  cv2.imwrite("02_blur.png", blur)

  _, threshold = cv2.threshold(
    blur, 0, 255,
    cv2.THRESH_BINARY+cv2.THRESH_OTSU
  )
  cv2.imwrite("03_threshold.png", threshold)

  kernel = np.ones((8, 8),np.uint8)
  opening = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)
  cv2.imwrite("04_opening.png", opening)

  closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
  cv2.imwrite("05_closing.png", closing)

  negated = cv2.bitwise_not(closing)
  cv2.imwrite("05__negated.png", negated)

  contours, hierarchy = cv2.findContours(
    negated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
  )
  blank_image_contours = np.zeros(img.shape, np.uint8)
  blank_image = np.zeros(img.shape, np.uint8)
  next_countour_indices = hierarchy[0,:,0]
  next_index = 0
  i = 0
  while next_index != -1:
    i += 1
    c = contours[next_index]
    cv2.drawContours(blank_image_contours, c, -1, (255, 0, 0), 5)
    x,y,w,h = cv2.boundingRect(c)

    print("Size: {0}  | ".format(w*h), (x,y), (x+w, y+h), (w, h))
    cv2.rectangle(blank_image, (x,y), (x+w,y+h), (r(), r(), r()), 10)
    next_index = next_countour_indices[next_index]

  print("Number of detected objects: {0}".format(i))
  cv2.imwrite("06_contours.png", blank_image_contours)
  cv2.imwrite("07_bounding_boxes.png", blank_image)
