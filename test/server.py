import tornado
import tornado.ioloop
import tornado.web
 
 
class FileUploadHandler(tornado.web.RequestHandler):
  def post(self):
    print(self.request.files)


application = tornado.web.Application([
  (r"/rawscan", FileUploadHandler),
], debug=True)


if __name__ == "__main__":
  application.listen(8912)
  tornado.ioloop.IOLoop.instance().start()

