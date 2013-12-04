#!/usr/bin/python

# Import modules for CGI handling
import cgi, cgitb 
import socket
import json
import sys
import os
import subprocess

cassini_ip = "192.168.56.1"
cassini_port = 7790

form = cgi.FieldStorage()
user_ip = form.getvalue("ip")
user_mac = form.getvalue("mac")
if os.environ:
  user_id = os.environ['REMOTE_USER'] or "foooo"


print "Content-type:text/html\r\n\r\n"
print '''
<html>
 <head>
  <title>Cassini MAC Registration Success</title>
 </head>
 <body>
  <h2>Cassini MAC Registration Suceeded</h2>
   <ul>
'''

print  "       <li>MAC address: %s</li>" % (user_mac,)
print  "       <li>IP address: %s</li>" % (user_ip,)
print  "       <li>User ID: %s</li>" % (user_id,)

if (user_id != "Unknown" and user_ip and user_mac):
  #send_nac_auth(cassini_ip,cassini_port,user_mac,user_ip,user_id)
  cmd = '/home/mininet/captive-portal/nac_test.py AUTH'
  #cmd = 'ls'

  # New process, connected to the Python interpreter through pipes:
  prog = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  prog.communicate()  # Returns (stdoutdata, stderrdata): stdout and stderr are ignored, here
  print prog
  if prog.returncode:
    raise Exception('program returned error code {0}'.format(prog.returncode))
  print "%s" % (cmd,)


print '''
 </body>
</html>
'''
