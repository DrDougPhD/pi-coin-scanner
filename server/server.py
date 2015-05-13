#!/usr/bin/env python
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Simplified chat demo for websockets.

Authentication, error handling, etc are left as an exercise for the reader :)
"""

import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid
import subprocess
import threading

from tornado.options import define
from tornado.options import options

define("port", default=8989, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/socket", ProgressSocketHandler),
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
        self.render("index.html", messages=ProgressSocketHandler.cache)

class ProgressSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    cache = []
    cache_size = 200

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        ProgressSocketHandler.waiters.add(self)
        print("Added one waiter")

    def on_close(self):
        ProgressSocketHandler.waiters.remove(self)
        print("Closed one waiter")

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
                if "html" not in chat:
                  chat["html"] = tornado.escape.to_basestring(
                    waiter.render_string("console_line.html", message=chat)
                  )
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

        ProgressSocketHandler.update_cache(chat)
        ProgressSocketHandler.send_updates(chat)


def ingot_split():
  #home_uri = os.path.expanduser("~kp")
  #directory = os.path.join(home_uri, "Warez", "Scans", "bars")
  
  p = subprocess.Popen(
    ["bash", "sleeper_message.sh"],#"bullionScanNMerge.sh", directory],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    universal_newlines=True,
  )
  while p.poll() is None:
    line = p.stdout.readline()
    update = {
      'id': str(uuid.uuid4()),
      'body': line,
    }
    ProgressSocketHandler.update_cache(update)
    ProgressSocketHandler.send_updates(update)
    print(line)

  # Process has terminated. Images can now be displayed.


class ImageProcessingHandler(tornado.web.RequestHandler):
  def get(self):
    split_and_merge_script = threading.Thread(
      target=ingot_split
    )
    split_and_merge_script.start()
    self.write("Message started")


def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
