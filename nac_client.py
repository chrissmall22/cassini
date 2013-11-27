#!/usr/bin/env python

# Copyright 2012 James McCauley
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This is NOT a POX component.  It's a little tool to test out the messenger.
"""

import socket
import json
import sys

def send_nac_auth (cassini_ip,cassini_port,user_mac,user_ip,user_id):
  print "Connecting to %s:%i" % (cassini_ip,cassini_port)
  port = int(cassini_port)
  
  state = sys.argv[1] or 'AUTH'
  print "Set MAC %s to state: %s" % (user_mac,state,)
  sock = socket.create_connection((cassini_ip, cassini_port))

  try:
    m = {}
    m['mac'] = user_mac
    m['ip'] = user_ip
    m['user'] = user_id
    m['CHANNEL'] = 'nac'
    m['state'] = state 
    m = json.dumps(m)
    sock.send(m)
    sock.shutdown(socket.SHUT_RDWR)    
    sock.close() 
  except:
      import traceback
      traceback.print_exc()
        




cassini_ip = "127.0.0.1"
cassini_port = 7790
user_mac = "00:00:00:00:00:01"
user_ip = "10.200.0.128"
user_id = "chsmall"

send_nac_auth(cassini_ip,cassini_port,user_mac,user_ip,user_id)
