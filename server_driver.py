import logging

logging.basicConfig(
  level=logging.DEBUG,
  filename='/tmp/server.log',
  filemode='w'
)
logger = logging.getLogger("piCoinScanner.server")
logger.addHandler(logging.StreamHandler())

import tornado
import tornado.ioloop
import tornado.web
from server import RawScanHandler
from server import MainHandler
from server import StatusSocketHandler
from server import IngotProcessorHandler


application = tornado.web.Application([
  (r"/",          MainHandler),
  (r"/rawscan",   RawScanHandler),
  (r"/ingotscan", IngotProcessorHandler),
  (r"/socket",    StatusSocketHandler),
], debug=True)


if __name__ == "__main__":
  try:
    application.listen(8912)
    tornado.ioloop.IOLoop.instance().start()
  
  except:
    logger.exception("Stuff didn't do")

