import tornado
import tornado.ioloop
import tornado.web
import os
import uuid
 
__UPLOADS__ = "uploads/"
 
class Userform(tornado.web.RequestHandler):
  def get(self):
    self.render("fileuploadform.html")
 
 
class Upload(tornado.web.RequestHandler):
  def post(self):
    fileinfo = self.request.files['filearg'][0]
    print("fileinfo is {0}".format(fileinfo))
    fname = fileinfo['filename']
    extn = os.path.splitext(fname)[1]
    cname = str(uuid.uuid4()) + extn
    fh = open(__UPLOADS__ + cname, 'w')
    fh.write(fileinfo['body'])
    self.finish(cname + " is uploaded!! Check {0} folder".format(__UPLOADS__))


application = tornado.web.Application([
  (r"/", Userform),
  (r"/upload", Upload),
], debug=True)


if __name__ == "__main__":
  application.listen(8888)
  tornado.ioloop.IOLoop.instance().start()
