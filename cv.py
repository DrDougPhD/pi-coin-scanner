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
    self.n = 1

  def __call__(self, img, name):
    plt.subplot(1,1, self.n)
    plt.imshow(img, 'gray')
    plt.title(name)
    plt.xticks([])
    plt.yticks([])
    self.n += 1


def to_monochrome(img):
  # Otsu's thresholding after Gaussian filtering
  blur = cv2.GaussianBlur(img, (5,5), 0)
  _, threshold = cv2.threshold(
    blur, 0, 255,
    cv2.THRESH_BINARY+cv2.THRESH_OTSU
  )

  opening = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, (5, 5))
  closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, (5, 5))

  return threshold
  

if __name__ == "__main__":
  img = cv2.imread(sys.argv[1])
  gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  plotter = SimplePlot()
  #plotter(img, "Initial")

  blur = cv2.GaussianBlur(gray_img, (5,5), 0)
  #plotter(blur, "Gaussian Blur")

  _, threshold = cv2.threshold(
    blur, 0, 255,
    cv2.THRESH_BINARY+cv2.THRESH_OTSU
  )
  #plotter(threshold, "Threshold")

  kernel = np.ones((5,5),np.uint8)
  opening = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)
  #plotter(opening, "Opening")

  closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
  #plotter(closing, "Opening")

  closing_inv = cv2.bitwise_not(closing)
  contours, hierarchy = cv2.findContours(closing_inv, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
  contour_img = img.copy()
  cv2.drawContours(contour_img, contours, 0, (0,255,0), 3)
  plotter(contour_img, "Contours")

  print(hierarchy)
  print("There are {0} contours".format(len(contours)))

  x,y,w,h = cv2.boundingRect(contours[0])
  cv2.rectangle(contour_img,(x,y),(x+w,y+h),(0,255,0),2)
  
  plt.show()
