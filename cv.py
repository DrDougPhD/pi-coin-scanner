import cv2
import numpy as np
import sys
from matplotlib import pyplot as plt

"""
# global thresholding
ret1,th1 = cv2.threshold(img,127,255,cv2.THRESH_BINARY)

# Otsu's thresholding
ret2,th2 = cv2.threshold(img,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
"""

class SimplePlot:
  def __init__(self):
    self.n = 0

  def __call__(self, img, name):
    plt.subplot(3,3,self.n)
    plt.imshow(img, 'gray')
    plt.title(name)
    plt.xticks([])
    plt.yticks([])


def to_monochrome(img):
  # Otsu's thresholding after Gaussian filtering
  blur = cv2.GaussianBlur(img, (5,5), 0)
  _, threshold = cv2.threshold(
    blur, 0, 255,
    cv2.THRESH_BINARY+cv2.THRESH_OTSU
  )
  return threshold
  

if __name__ == "__main__":
  img = cv2.imread(sys.argv[1])
  gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  plotter = SimplePlot()

  threshold = to_monochrome(gray_img)
  plotter(threshold, "Otsu Thresholding")

  plt.show()
