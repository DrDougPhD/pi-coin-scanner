# Doug McGeehan (djmvfb@mst.edu)
# Bouncing-eliminating BinaryState object.

import time


class BinaryState:
  """Prevent bouncing of the signal when the button is pressed."""

  def __init__(self, initial_state=0):
    self.state = initial_state

  def has_changed(self, i):
    return i != self.state

  def set(self, i):
    self.state = i
    time.sleep(0.05)

  def __bool__(self):
    return bool(self.state)

  __nonzero__=__bool__

