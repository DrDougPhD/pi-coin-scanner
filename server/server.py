import logging
logger = logging.getLogger("piCoinScanner.server")

import tornado
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid

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


class RawScanHandler(tornado.web.RequestHandler):
  def post(self):
    print(self.request.files.keys())
    
    # Split the image files.
    # Store the split images in temporary files.
    # Increment the state.
    # If the state has returned to 0 (or 2)
    #   Merge the corresponding files.
    #   Export merged files to permanent files.
    #   (TODO) Wait for approval of files to re-attempt splitting and merging.

class IngotProcessorHandler(tornado.web.RequestHandler):
  def post(self):
    print(self.request.files.keys())
