class ImageMerger:
  def __init__(self, session_dir):
    self.session_dir = session_dir

  def __call__(self, obverse, reverse):
    print("Merging {0} and {1}".format(obverse, reverse))
    return "NOT IMPLEMENTED YET"
