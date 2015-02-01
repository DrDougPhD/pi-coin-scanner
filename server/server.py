import logging
logger = logging.getLogger("piCoinScanner.server")
from datetime import datetime
import tornado
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid
import threading
import subprocess
import shutil
from splitter import MultiCrop
from merger import ImageMerger
from tornado.options import define
from tornado.options import options
 
define("port", default=8989, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/socket", StatusSocketHandler),
            (r"/execute", ImageProcessingHandler),
        ]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
  def get(self):
    self.render("index.html", messages=StatusSocketHandler.cache)


class StatusSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    cache = []
    cache_size = 200

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        StatusSocketHandler.waiters.add(self)

    def on_close(self):
        StatusSocketHandler.waiters.remove(self)

    @classmethod
    def update_cache(cls, chat):
        cls.cache.append(chat)
        if len(cls.cache) > cls.cache_size:
            cls.cache = cls.cache[-cls.cache_size:]

    @classmethod
    def send_updates(cls, chat):
        logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(chat)
            except:
                logging.error("Error sending message", exc_info=True)

    def on_message(self, message):
        logging.info("got message %r", message)
        parsed = tornado.escape.json_decode(message)
        chat = {
            "id": str(uuid.uuid4()),
            "body": parsed["body"],
        }
        chat["html"] = tornado.escape.to_basestring(
            self.render_string("message.html", message=chat)
        )

        StatusSocketHandler.update_cache(chat)
        StatusSocketHandler.send_updates(chat)

RAW_FILE_STORAGE = "/home/kp/Warez/Scans"

class RawScanHandler(tornado.web.RequestHandler):
  def put(self):
    print("SHOULD NOT BE POSTING HERE")
    print(dir(self.request))
    print(type(self.request))
    print("Size of self.request.body: {0} chars".format(len(self.request.body)))
    
    # Split the image files.
    # Store the split images in temporary files.
    # Increment the state.
    # If the state has returned to 0 (or 2)
    #   Merge the corresponding files.
    #   Export merged files to permanent files.
    #   (TODO) Wait for approval of files to re-attempt splitting and merging.

class IngotProcessorHandler(tornado.web.RequestHandler):
  images = None

  def put(self):
    print("#"*80)
    if IngotProcessorHandler.images is None:
      print("Obverse image received!")
      print("-----------------------")
      IngotProcessorHandler.images = IngotProcessor(
        obverse_img=self.request
      )
      splitter = threading.Thread(
        target=IngotProcessorHandler.images.splitObverse
      )
      splitter.start()

    else:
      print("Reverse image received!")
      print("-----------------------")
      IngotProcessorHandler.images.addReverse(self.request)
      merger = threading.Thread(
        target=IngotProcessorHandler.images.merge
      )
      merger.start()

      IngotProcessorHandler.images = None


class IngotProcessor:
  STORAGE_DIR = os.path.join(RAW_FILE_STORAGE, "Bars")
  DATETIME_FMT = "%Y-%m-%d %Hh %Mm %Ss"
  SPLIT_EXT = ".tiff"
  MERGE_EXT = ".jpg"
   
  def __init__(self, obverse_img):
    self.session_id = datetime.now().strftime(IngotProcessor.DATETIME_FMT)

    # Make session directories for output scans.
    print("Session directory at {0}".format(self.getSessionDirname()))
    os.makedirs(self.getSessionDirname())
    self.splitter = MultiCrop(self.getSessionDirname())
    self.merger   = ImageMerger(self.getSessionDirname())

    # Write file to disk.
    self.obverse_path = self._write(img=obverse_img, is_obverse=True)

  def addReverse(self, reverse_img):
    # Write file to disk.
    self.reverse_path = self._write(img=reverse_img, is_obverse=False)

  def splitObverse(self):
    """This is called by the server to split the obverse image."""
    print("Splitting obverse image")
    self.splitter(
      img=self.obverse_path,
      is_obverse=True,
    )

  def _write(self, img, is_obverse):
    filename = "{0}.tiff".format("obverse" if is_obverse else "reverse")
    path = os.path.join(self.getSessionDirname(), filename)
    print("Writing file to {0}".format(path))
    with open(path, 'w') as f:
      f.write(img.body)
    print("Finished writing file")
    return path

  def merge(self):
    print("Splitting reverse image")
    self.splitter(
      img=self.reverse_path,
      is_obverse=False,
    )
    print("Merging split images")
    for o, r in self.splitter:
      result = self.merger(
        obverse=o,
        reverse=r,
      )
      print("{0} and {1} merged to {2}".format(o, r, result))

  def getSessionDirname(self):
    return os.path.join(
      IngotProcessor.STORAGE_DIR,
      self.session_id
    )

