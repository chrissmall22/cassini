#!/usr/bin/python

# Import modules for CGI handling
import cgi, cgitb 
import socket
import json
import sys
import os

def send_nac_auth (cassini_ip,cassini_port,user_mac,user_ip,user_id):
  #print "<p>Connecting to %s:%i</p>" % (cassini_ip,cassini_port)
  ip = str(cassini_ip)
  port = int(cassini_port)

  state = 'AUTH'
  print "<p>Set MAC %s to state: %s</p>" % (user_mac,state,)

  #s = socket.create_connection((cassini_ip, port))


  m = {}
  m['mac'] = user_mac
  m['ip'] = user_ip
  m['user'] = user_id
  m['CHANNEL'] = 'nac'
  m['state'] = state

  m = json.dumps(m)
  print "<pre> JSON: \n %s </pre>" % (m,)

  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  print "<p>Connecting to %s:%i</p>" % (ip,port)
  s.connect((ip,port))
  print "<p>Sending to %s:%i</p>" % (ip,port)
  

  s.send(m)
  result = json.loads(s.recv(1024))
  print "<pre> result JSON: \n %s </pre>" % (m,)
  sock.close()

cassini_ip = "192.168.56.1"
cassini_port = 7790


form = cgi.FieldStorage()
user_ip = form.getvalue("ip")
user_mac = form.getvalue("mac")
user_id = os.environ['REMOTE_USER'] 
#user_id = "Unknown"


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

if (user_id != "Unknown" and user_ip and user_mac):
  send_nac_auth(cassini_ip,cassini_port,user_mac,user_ip,user_id)
  print "send_nac_auth(%s,%d,%s,%s,%s)" % (cassini_ip,cassini_port,user_mac,user_ip,user_id)


print '''
 </body>
</html>
'''
