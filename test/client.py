# Doug McGeehan (djmvfb@mst.edu)
import subprocess
import requests


if __name__ == "__main__":
  print("Scanning image...")
  shell_cmds = ["ls"]
  with subprocess.Popen(shell_cmds, stdout=subprocess.PIPE) as p:
    url = 'http://localhost:8912/rawscan'
    scanned_image = {
      'file': ('scan.tiff', p.stdout.read())
      #'file': p.stdout
    }
    r = requests.post(url, files=scanned_image)
  print("Done")

