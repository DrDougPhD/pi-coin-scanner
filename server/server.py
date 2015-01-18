import web
import subprocess
import os

        
urls = (
  '/(.*)', 'hello'
)
app = web.application(urls, globals())


class hello:        
  def GET(self, filename_prefix):
    home_uri = os.path.expanduser("~kp")
    directory = os.path.join(home_uri, "Warez", "Scans", "bars")
    
    subprocess.Popen([
      "bash", "bullionScanNMerge.sh", directory
    ])

    return '{0}'.format(directory)


if __name__ == "__main__":
  app.run()

