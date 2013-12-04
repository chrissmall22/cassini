#!/usr/bin/env python
# coding: utf-8

import pyjsonrpc
import json



def send_nac_auth (ip,user_mac,user_ip,user_id):

  cassini_url = 'http://' + ip + ':8000/_jrpcmsg/'
  print "Connecting to AJAX server at %s" % (cassini_url,)

  state = 'REG'

  http_client = pyjsonrpc.HttpClient(
    url = cassini_url ,
    username = 'cassini',
    password = 'cassini'
  )

  m = {}
  n = {}
  m['mac'] = user_mac
  m['ip'] = user_ip
  m['user'] = user_id
  m['CHANNEL'] = 'nac'
  m['state'] = state 
  n['session_id'] = 'new!'
  n['msg'] = "foo" 
  
  n = json.dumps(n)
  print http_client.send('new!',m)



cassini_ip = "192.168.56.1"
user_mac = "00:00:00:00:00:01"
user_ip = "10.200.0.128"
user_id = "chsmall"

send_nac_auth(cassini_ip,user_mac,user_ip,user_id)
