#!/usr/bin/env python3

import sys
import json
from apscheduler.schedulers.background import BackgroundScheduler
from pathlib import Path
from pprint import pprint

from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import socketserver
from ring_doorbell import Ring, Auth
from oauthlib.oauth2 import MissingTokenError

ring = None
cache_file = Path("data/token.cache")


class S(BaseHTTPRequestHandler):
  def _set_response(self):
    self.send_header('Content-type', 'application/json')
    self.end_headers()

  def do_GET(self):
    self.send_response(404)
    self._set_response()
    self.wfile.write(b'{"error":404}')

  def do_POST(self):
    post_data = '{}'
    if 'Content-Length' in self.headers:
      content_length = int(self.headers['Content-Length'])
      post_data = self.rfile.read(content_length).decode('utf-8')
    if str(self.path) == '/chime':
      dochime(json.loads(post_data))
      self.send_response(200)
      self._set_response()
      self.wfile.write(b'{"result":"ok"}')
    else:
      self.send_response(404)
      self._set_response()
      self.wfile.write(b'{"error":404}')

  def do_PUT(self):
    self.send_response(404)
    self._set_response()
    self.wfile.write(b'{"error":404}')


def main():
  global cache_file, token_updated, ring
  if not cache_file.is_file():
    print("Token not found", file=sys.stderr)
    exit(1)

  print("Instantiating ring api...")
  auth = Auth(user_agent="SmartThingsApi/0.1", token=json.loads(cache_file.read_text()), token_updater=token_updated)
  ring = Ring(auth)
  ring.update_data()
  print("Instantiating background job...")
  scheduler = BackgroundScheduler()
  scheduler.add_job(pingring, 'interval', hours=2)
  scheduler.start()
  print("Starting web server...")
  run()


def token_updated(token):
  global cache_file
  print("Updating ring token...")
  cache_file.write_text(json.dumps(token))


def pingring():
  global ring
  print("Updating ring data...")
  ring.update_data()


def dochime(postdata):
  global ring
  chime = 'ding'
  if postdata and postdata['kind']:
    chime = postdata['kind']

  if chime == 'off':
    print("Got off -event - no action...")
    return

  devices = ring.devices()
  print("Playing chime '" + chime + "'...")
  # devices['chimes'][0].volume = 2
  devices['chimes'][0].test_sound(kind=chime)


def run(server_class=HTTPServer, handler_class=S):
  logging.basicConfig(level=logging.INFO)
  server_address = ('0.0.0.0', 8000)
  httpd = server_class(server_address, handler_class)
  httpd.serve_forever()


main()

