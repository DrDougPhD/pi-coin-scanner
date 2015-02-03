# Doug McGeehan (djmvfb@mst.edu)
import sys
if len(sys.argv) < 3:
  print("ERROR: must include the path to the obverse and reverse images as parameters")
  sys.exit(1)

import os
import RPi.GPIO as GPIO
from pi import BinaryState
import time
import httplib
import uuid
import subprocess


# Set labeled pin 18 to input. This is physical pin 12.
SERVER_ADDR="power"
SERVER_PORT=8912
SERVER_PATH="/ingotscan"
EXT = "tiff"
SCANNER_ADDR="hpaio:/usb/Deskjet_F4100_series?serial=CN7CM6G1Q104TJ"
TMP_DIR="/home/pi/Warez/Scans/bars/"

def upload_image_to_url(addr, port, upload_url, img_url):
  if upload_url[0] != "/":
    upload_url = "/"+upload_url

  print("Opening HTTP connection with http://{0}:{1}{2}".format(
    addr, port, upload_url
  ))
  conn = httplib.HTTPConnection(addr, port)
  conn.request("PUT", upload_url, open(img_url, 'rb'))
  response = conn.getresponse()
  conn.close()


if __name__ == "__main__":
  obverse_img = sys.argv[1]
  print("Obverse image: {0}".format(obverse_img))
  reverse_img = sys.argv[2]
  print("Reverse image: {0}".format(reverse_img))

  """
  start = time.time()
  #r = requests.post(url, files=scanned_image)
  upload_image_to_url(
    addr=SERVER_ADDR, port=SERVER_PORT, upload_url=SERVER_PATH,
    img_url=obverse_img,
  )
  duration = time.time() - start
  print("Uploading took {0} seconds".format(duration))
  """
