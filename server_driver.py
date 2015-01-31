import logging

logging.basicConfig(
  level=logging.INFO,
  filename='/tmp/server.log',
  filemode='w'
)
logger = logging.getLogger("piCoinScanner.server.driver")


import tornado.ioloop
import tornado.web
from server import FileUploadHandler
from server import MainHandler
from server import StatusSocketHandler


application = tornado.web.Application([
  (r"/",          MainHandler),
  (r"/rawscan",   FileUploadHandler),
  (r"/socket",    StatusSocketHandler),
], debug=True)


if __name__ == "__main__":
  try:
    application.listen(8912)
    tornado.ioloop.IOLoop.instance().start()
  
  except:
    logger.exception("Stuff didn't do")

