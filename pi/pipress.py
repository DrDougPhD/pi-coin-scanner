# Doug McGeehan (djmvfb@mst.edu)
# Based on code from Physical computing with Raspberry Pi: Buttons and Switches, University of Cambridge.
#  https://www.cl.cam.ac.uk/projects/raspberrypi/tutorials/robot/buttons_and_switches/
#
# Simple script that will display a message when a button is pressed on the Raspberry Pi.

import RPi.GPIO as GPIO
import time
import datetime
import subprocess
import os
from unique_files import create_unique_filename
from binarystate import BinaryState


# Set labeled pin 18 to input. This is physical pin 12.
GPIO.setmode(GPIO.BCM)
BUTTON_PIN = 18
GPIO.setup(BUTTON_PIN, GPIO.IN)

TOGGLE_PIN = 17
GPIO.setup(TOGGLE_PIN, GPIO.IN)


# Define image format / extension. tiff and jpg works. Some others may, but
#  not tested.
EXT="tiff"


def simplescan():
  home_uri = os.path.expanduser("~pi")
  directory = os.path.join(home_uri, "Warez", "Scans")
  filename_suffix = str(datetime.date.today())
  uri = create_unique_filename(directory=directory, suffix=filename_suffix, ext=EXT)

  print("Scanning image to {0}".format(uri))
  with open(uri, 'w') as f:
    subprocess.call([
      "scanimage",
      "--device-name", "hpaio:/usb/Deskjet_F4100_series?serial=CN7CM6G1Q104TJ",
      "--resolution", "300",
      "--format", EXT,
    ], stdout=f)
  print("Done")


def ingotscan(is_reverse):
  home_uri = os.path.expanduser("~pi")
  directory = os.path.join(home_uri, "Warez", "Scans", "bars")
  filename_suffix = str(datetime.date.today())
  uri = create_unique_filename(directory=directory, suffix=filename_suffix, ext=EXT)

  print("Scanning image to {0}".format(uri))
  with open(uri, 'w') as f:
    subprocess.call([
      "scanimage",
      "--device-name", "hpaio:/usb/Deskjet_F4100_series?serial=CN7CM6G1Q104TJ",
      "--resolution", "300",
      "--format", EXT,
    ], stdout=f)
  print("Done")
  return uri


def ingotsplit(img_urls):
  directory = os.path.dirname(img_urls[0])
  print("Splitting images")
  subprocess.call([
    "bash", "bullionScanNMerge.sh", directory
  ])
  print("Done splitting images")


class TrinaryState:
  def __init__(self, init_state=0):
    self.state = init_state

  def transition_to_next_state(self):
    self.state = (self.state+1) % 3

  def is_initial_state(self):
    return (self.state == 0)

  def is_middle_state(self):
    return (self.state == 1)

  def is_ending_state(self):
    return (self.state == 2)


if __name__ == "__main__":
  os.setgid(1000)
  os.setuid(1000)
  state = BinaryState()
  toggle = BinaryState(GPIO.input(TOGGLE_PIN))
  ingot_scanning_state = TrinaryState()
  ingot_scanned_images = [None, None]

  while True:
    i = GPIO.input(BUTTON_PIN)
    b = GPIO.input(TOGGLE_PIN)

    if bool(toggle):
      # Silver ingot scanning is underway.
      if not ingot_scanning_state.is_ending_state():
        if state.has_changed(i) and i:
          if ingot_scanning_state.is_initial_state():
            print("Scanning obverse")
            img_url = ingotscan()
            ingot_scanned_images[0] = img_url

          else:
            print("Scanning reverse")
            img_url = ingotscan()
            ingot_scanned_images[1] = img_url

          ingot_scanning_state.transition_to_next_state()

      else:
        # Two images have been scanned. Time to split them up.
        ingotsplit(ingot_scanned_images)
        ingot_scanning_state.transition_to_next_state()
      
    else:
      # Perform a simple scan.
      if state.has_changed(i) and i:
        simplescan()


    if toggle.has_changed(b):
      if b:
        print("Ingot scanning engaged.")
      else:
        print("Simple scanning engaged.")


    toggle.set(b)
    state.set(i)



