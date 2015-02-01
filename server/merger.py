import subprocess
import os

class ImageMerger:
  MERGE_EXT = ".jpg"

  def __init__(self, session_dir):
    self.filename_suffix = os.path.basename(session_dir)
    self.destination_dir = os.path.dirname(session_dir)
    self.num = 0

  def __call__(self, obverse, reverse):
    print("Merging {0} and {1}".format(obverse, reverse))
    destination_file = os.path.join(
      self.destination_dir,
      "{0}_{1}{2}".format(
        self.filename_suffix, self.num, ImageMerger.MERGE_EXT
    ))
    p = subprocess.Popen([
        "bash", "imgmerge.sh",
        obverse, reverse,
        destination_file
      ],
      stdout=subprocess.PIPE,
      stderr=subprocess.STDOUT,
      universal_newlines=True,
    )

    while p.poll() is None:
      line = p.stdout.readline().strip()
      print(line)
    print("="*80)

    self.num += 1
    return destination_file
