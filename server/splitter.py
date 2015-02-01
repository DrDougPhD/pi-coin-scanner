import logging
logger = logging.getLogger("piCoinScanner.server.splitter")

import subprocess
import shutil
import os
import uuid

class MultiCrop:
  SPLIT_EXT = ".tiff"

  def __init__(self, session_dir):
    self.session_dir = session_dir
    self.images = {"obverse": None, "reverse": None}

  def __call__(self, img, is_obverse):
    # multicrop -c West -u 3 -f 15 "$f" "${TMP_DIR}/${img_filename}"
    tmp_dir = self._getTempDirectory()
    tmp_destination = self._getMulticropDestination(tmp_dir, is_obverse)
    destination_dir = self.getDirname(is_obverse)
    print("Images will be output to {0}".format(destination_dir))
    p = subprocess.Popen([
        "./multicrop",
        '-c', 'West',
        '-u', '3',
        '-f', '15',
        img, tmp_destination
      ],
      stdout=subprocess.PIPE,
      stderr=subprocess.STDOUT,
      universal_newlines=True,
    )

    while p.poll() is None:
      line = p.stdout.readline().strip()
      update = {
        'id': str(uuid.uuid4()),
        'body': line,
      }
      print(line)
    print("="*80)
    # Process has terminated. Images can now be displayed.
    shutil.move(tmp_dir, destination_dir)

    # Pair together the corresponding obverse and reverse images
    self._populate(is_obverse, destination_dir)

  def _getTempDirectory(self):
    directory = os.path.join("/tmp", str(uuid.uuid4()))
    os.makedirs(directory)
    return directory

  def _getMulticropDestination(self, tmp_dir, is_obverse):
    return os.path.join(tmp_dir, "{0}{1}".format(
      "o" if is_obverse else "r", MultiCrop.SPLIT_EXT
    ))

  def getDirname(self, is_obverse):
    return os.path.join(
      self.session_dir,
      "obverse" if is_obverse else "reverse",
    )

  def _populate(self, is_obverse, destination_dir):
    key = "obverse" if is_obverse else "reverse"
    images = []
    for f in os.listdir(destination_dir):
      filepath = os.path.join(destination_dir, f)
      if os.path.isfile(filepath) and f.endswith(MultiCrop.SPLIT_EXT):
        images.append(filepath)
    images.sort()

    self.images[key] = images
    print("Files found: {0}".format(images))

  def __iter__(self):
    for pair in zip(self.images["obverse"], self.images["reverse"]):
      yield pair
