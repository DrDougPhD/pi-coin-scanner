# Doug McGeehan (djmvfb@mst.edu)
#
# At this moment, I need to fake some behavior from the client to finish up
#  some work on the server. The work on the server is the automatic processing
#  of two images, scanned one after another, so that they are split and then
#  recombined when both images have been received.
#
# Here is the simple workflow.
#
#  1. User places ingots obverse-side down on the scanner.
#  2. User engages ingot button (self locking button).
#  2.5  User tells Pi how many ingots are on the scanner.
#  3. User presses scan button.
#  4. Pi scans image, saves to memory.
#  5. Because ingot button is engaged, Pi submits scanned image to server
#      through IngotProcessing URL POST.
#      Pi also submits the number of expected ingots.
#  6. Server receives image through IngotProcessor POST.
#  7. Server observes this is the first image received. Thus no merging will
#      occur.
#  8. Server automatically splits image, and saves split images somewhere.
#  8.5  If the number of images split does not equal the number expected,
#        the server will modify its threshold for splitting.
#  9. Server now waits for second image.
# 10. User flips ingots to reverse-side down on the scanner.
# 11. User presses scan button.
# 12. Pi scans image, saves to memory.
# 13. Because ingot button is engaged, Pi submits scanned image to server
#      through IngotProcessor POST.
# 14. Server receives image through IngotProcessor POST.
# 15. Server observes this is the second image received. Thus, it will perform
#      merging...
# 16. Server splits image, and saves the split images somewhere.
# 16.5  If the number of images split does not equal the number expected,
#        the server will modify its threshold for splitting.
# 17. Because this is the second image received, the server will begin
#      merging of images. Merged images will be stored somewhere permanent.
#
#
#  What happens if the splitting is all wrong?
#   -> The server should keep the raw copies of the images stored in case
#       splitting is all wrong.
#   -> The Raspberry Pi should have two buttons to determine if scanning
#       was done correctly.
#        1. Raspberry Pi receives async signal from Server that merging is
#            is complete.
#        1. Pi asks user if images are satisfactory, waiting for button
#            press.
#        1. User reviews images.
#        1. If satisfactory, User presses Accept button.
#        1.   Raspberry Pi sends confirmation signal back to server.
#        1.   Server permanently stores merged images.
#        1.   Server deletes intermediate images.
#        1. If unsatisfactory, User presses Retry button.
#        1.   Raspberry Pi sends retry signal back to server.
#        1.   Server begins splitting and merging operation again.
#            
#            
#
import os
import RPi.GPIO as GPIO
from pi import BinaryState
import requests
import time

# Set labeled pin 18 to input. This is physical pin 12.
GPIO.setmode(GPIO.BCM)
BUTTON_PIN = 18
GPIO.setup(BUTTON_PIN, GPIO.IN)

TOGGLE_PIN = 17
GPIO.setup(TOGGLE_PIN, GPIO.IN)

SAMPLE_FILE="/home/pi/2014-12-28_0.tiff"


if __name__ == "__main__":
  os.setgid(1000)
  os.setuid(1000)
  state = BinaryState()
  toggle = BinaryState(GPIO.input(TOGGLE_PIN))

  while True:
    i = GPIO.input(BUTTON_PIN)
    b = GPIO.input(TOGGLE_PIN)

    if state.has_changed(i) and i:
      print("#"*80)
      if bool(toggle):
        # Silver ingot scanning is underway.
        print("Scanning ingot")
        url = 'http://power:8912/rawscan'

        with open(SAMPLE_FILE) as f:
          scanned_image = {
            'file': ('scan.tiff', f.read())
          }

        start = time.time()
        r = requests.post(url, files=scanned_image)
        duration = time.time() - start
        print("Uploading took {0} seconds".format(duration))

    else:
      # Perform a simple scan.
      print("Scanning document")


    if toggle.has_changed(b):
      if b:
        print("Ingot scanning engaged.")
      else:
        print("Simple scanning engaged.")


    toggle.set(b)
    state.set(i)


