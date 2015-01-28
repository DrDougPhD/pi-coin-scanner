import subprocess
import requests
import logging
logger = logging.getLogger("pipress.scancontrol")

class BaseScanner:
  shell_cmds = [
    "scanimage",
    "--device-name", "hpaio:/usb/Deskjet_F4100_series?serial=CN7CM6G1Q104TJ",
    "--resolution", "300",
    "--format", "tiff"
  ]

  
  def __call__(self):
    start = time.time()
    with subprocess.Popen(self.shell_cmds, stdout=subprocess.PIPE) as p:
      scanned_image = {
        'file': ('scan.tiff', p.stdout.read())
        #'file': p.stdout
      }
      duration = time.time() - start
      logging.info("Scanner returned image in {0} seconds".format(duration))

      url = self.getHTTPPOSTURL()

      post_start = time.time()
      r = requests.post(url, files=scanned_image)
      post_duration = time.time() - post_start
      logger.info("Image POSTed to {0} in {1} seconds".format(
        url, post_duration
      ))
      # Don't log the raw binary.
      try:
        r.pop("files", None)
      except:
        logger.exception("Popping binary data from POST response resulting"
                          " in an error")
      logger.debug(r)



  def getHTTPPOSTURL(self):
    """Classes extending the BaseScanner abstract class must uniquely specify
    the HTTP POST url to where the scanned image is to be uploaded."""

    raise NotImplementedError(
      "Class '{0}' does not implement the getHTTPPOSTURL() method inherited"
      " from the BaseScanner abstract class".format(
      self.__class__.__name__
    ))


class MultidocumentScanner(BaseScanner):
  """The MultidocumentScanner should be used when multiple documents
  are placed on a scanner bed at the same time. Calling an instance of
  this class will instantiate the chain reaction that will separate these
  documents into the individual constituent images automatically."""

  def __call__(self):
    


if __name__ == "__main__":
  x = BaseScanner()
  x()
