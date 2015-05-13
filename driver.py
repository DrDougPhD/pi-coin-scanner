# Doug McGeehan (djmvfb@mst.edu)
# Based on code from Physical computing with Raspberry Pi: Buttons and Switches, University of Cambridge.
#  https://www.cl.cam.ac.uk/projects/raspberrypi/tutorials/robot/buttons_and_switches/
#
# Simple script that will display a message when a button is pressed on the Raspberry Pi.

import RPi.GPIO as GPIO
from datetime import datetime
import subprocess
import os
from unique_files import create_unique_filename
from binarystate import BinaryState
from trinarystate import TrinaryState
from cv import img2bounding_box
from process import splitAndMerge

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


# Set labeled pin 18 to input. This is physical pin 12.
GPIO.setmode(GPIO.BCM)
BUTTON_PIN = 18
GPIO.setup(BUTTON_PIN, GPIO.IN)

TOGGLE_PIN = 17
GPIO.setup(TOGGLE_PIN, GPIO.IN)


# Define image format / extension. tiff and jpg works. Some others may, but
#  not tested.
EXT="tiff"
BORDER_REDUCTION=50
OUTPUT_DIRECTORY = "."
RAW_DIRECTORY = os.path.join(OUTPUT_DIRECTORY, "raw")
INTERMEDIATE_IMAGE_DIRECTORY = os.path.join(OUTPUT_DIRECTORY, "intermediate")
CROPPED_IMAGE_DIRECTORY = os.path.join(OUTPUT_DIRECTORY, "cropped")
MERGED_OUTPUT_DIRECTORY = os.path.join(
  os.path.expanduser("~pi"),
  "Warez", "Scans", "bars"
)


def simplescan():
  home_uri = os.path.expanduser("~pi")
  directory = os.path.join(home_uri, "Warez", "Scans")
  filename_suffix = str(datetime.now().date())
  uri = create_unique_filename(directory=directory, suffix=filename_suffix, ext=EXT)

  logger.info("Scanning image to {0}".format(uri))
  start = datetime.now()
  with open(uri, 'w') as f:
    subprocess.call([
      "scanimage",
      "--device-name", "hpaio:/usb/Deskjet_F4100_series?serial=CN7CM6G1Q104TJ",
      "--resolution", "300",
      "--format", EXT,
    ], stdout=f)

  duration = datetime.now() - start
  logger.info("Scanning complete in {0}".format(duration))


def ingotscan(is_reverse):
  directory = RAW_DIRECTORY
  if not os.path.exists(directory):
    os.makedirs(directory)

  filename_suffix = datetime.now().date().isoformat()
  uri = create_unique_filename(directory=directory, suffix=filename_suffix, ext=EXT)

  logger.info("Scanning image to {0}".format(uri))
  start = datetime.now()
  with open(uri, 'w') as f:
    subprocess.call([
      "scanimage",
      "--device-name", "hpaio:/usb/Deskjet_F4100_series?serial=CN7CM6G1Q104TJ",
      "--resolution", "300",
      "--format", EXT,
    ], stdout=f)
  duration = datetime.now() - start
  logger.info("Scanning complete in {0}".format(duration))
  return uri


if __name__ == "__main__":
  os.setgid(1000)
  os.setuid(1000)
  state = BinaryState()
  toggle = BinaryState(GPIO.input(TOGGLE_PIN))
  ingot_scanning_state = TrinaryState()
  ingot_scans = [None, None]

  while True:
    i = GPIO.input(BUTTON_PIN)
    b = GPIO.input(TOGGLE_PIN)

    if bool(toggle):
      # Silver ingot scanning is underway.
      if not ingot_scanning_state.is_ending_state():
        if state.has_changed(i) and i:
          if ingot_scanning_state.is_initial_state():
            logger.info("Scanning obverse")
            img_url = ingotscan(is_reverse=False)
            obverse = img2bounding_box(
              url=img_url, border_reduction=BORDER_REDUCTION,
              intermediate_destination=INTERMEDIATE_IMAGE_DIRECTORY,
              cropped_destination=CROPPED_IMAGE_DIRECTORY,
            )
            ingot_scans[0] = obverse

          else:
            logger.info("Scanning reverse")
            img_url = ingotscan(is_reverse=True)
            reverse = img2bounding_box(
              url=img_url, border_reduction=BORDER_REDUCTION,
              intermediate_destination=INTERMEDIATE_IMAGE_DIRECTORY,
              cropped_destination=CROPPED_IMAGE_DIRECTORY,
            )
            ingot_scans[1] = reverse

          ingot_scanning_state.transition_to_next_state()

      else:
        # Two images have been scanned. Time to split them up.
        logger.info("Merging split images")
        obverse, reverse = ingot_scans
        merged_images = splitAndMerge(
          obverse, reverse,
          MERGED_OUTPUT_DIRECTORY
        )
        logger.info("{0} merged images created".format(len(merged_images)))
        logger.info("\n".join(merged_images))
        ingot_scanning_state.transition_to_next_state()
      
    else:
      # Perform a simple scan.
      if state.has_changed(i) and i:
        logger.info("Simple scan")
        #simplescan()


    if toggle.has_changed(b):
      if b:
        logger.info("Ingot scanning engaged.")
      else:
        logger.info("Simple scanning engaged.")


    toggle.set(b)
    state.set(i)

