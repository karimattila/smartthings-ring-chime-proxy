#!/usr/bin/env python3

import json
import getpass
from pathlib import Path

from ring_doorbell import Ring, Auth
from oauthlib.oauth2 import MissingTokenError

cache_file = Path("data/token.cache")

def token_updated(token):
  cache_file.write_text(json.dumps(token))

def otp_callback():
  auth_code = input("2FA code: ")
  return auth_code

def login():
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    auth = Auth(user_agent="SmartThingsApi/0.1", token_updater=token_updated)
    try:
      auth.fetch_token(username, password)
    except MissingTokenError:
      auth.fetch_token(username, password, otp_callback())

  ring = Ring(auth)
  ring.update_data()
  devices = ring.devices()
  print(str(devices))
  print("Success...")

login()
