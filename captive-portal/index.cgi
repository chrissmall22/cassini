#!/usr/bin/python

# Import modules for CGI handling
import cgi, cgitb 
import socket
import pyjsonrpc
import json
import sys
import os
import urllib2

def send_nac_auth (ip,user_mac,user_ip,user_id):

  cassini_url = 'http://' + ip + ':8000/_jrpcmsg/'
  
  print "<p>Connecting to AJAX server at %s</p>" % (cassini_url,)

  state = 'AUTH'

  http_client = pyjsonrpc.HttpClient(
    url = cassini_url ,
    username = 'cassini',
    password = 'cassini'
  )
  
  m = {}
  m['mac'] = user_mac
  m['ip'] = user_ip
  m['user'] = user_id
  m['CHANNEL'] = 'nac'
  m['state'] = state 

  
  http_client.send('new!',m)
  if response.error:
     print "Error:", response.error.code, response.error.message
  else:
     print "Result:", response.result
    


cassini_ip = '140.142.21.80'

form = cgi.FieldStorage()
user_ip = form.getvalue("ip")
user_mac = form.getvalue("mac")
user_id = os.environ['REMOTE_USER'] 
#user_mac = "00:00:00:00:00:01"
#user_ip = '10.200.0.1'
#user_id = 'foo'


print "Content-type:text/html\r\n\r\n"
print '''
<html>
 <head>
  <title>Cassini Authentication Success</title>
 </head>
 <body>
  <h2>Cassini Authentication Suceeded</h2>
   <ul>
'''

print  "       <li>MAC address: %s</li>" % (user_mac,)
print  "       <li>IP address: %s</li>" % (user_ip,)
print  "       <li>User ID: %s</li>" % (user_id,)

print "   <pre>"

if (user_id != "Unknown" and user_ip and user_mac):
  send_nac_auth(cassini_ip,user_mac,user_ip,user_id)


print '''
  </pre>
 </body>
</html>
'''
