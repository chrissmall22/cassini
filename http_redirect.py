# Copyright 2013 Christopher Small

"""
Cassini - Network Access Control Application

A rewrite of the Resonance Network Access Control Application in PoX
Built to work with the Cassini Network Edge Manager 

While using some of the logic this is a rewrite with a DB and web interface view 
to be closly integrated


Simple test of Http redirection -

If a request goes out create a packet_out and redirect to new url (i.e. captive portal)
"""

import os 
from pox.core import core
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt
from pox.lib.util import dpid_to_str
from pox.lib.util import str_to_bool
from pox.lib.addresses import IPAddr, EthAddr

from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime


from cassini.db import nac_db, model_orm
from cassini.db.nac_db import *

import socket

#import mysql.connector

log = core.getLogger()

HTTP_PORT = 80

class HttpRedirect (object):
  """
  Waits for OpenFlow switches to connect.
  """
  
  def __init__ (self, transparent):
    core.openflow.addListeners(self)
    self.transparent = transparent


   
   
  def _handle_ConnectionUp (self, event):
    log.debug("Connection %s" % (event.connection,))
    push_default_rules(event)
    push_trusted_macs(event)

  def _handle_ConnectionDown (self, event):
    log.debug("Connection %s" % (event.connection,))
             



  def _handle_PacketIn (self, event):
    packet = event.parsed
    
    log.debug("PacketIn Connection %s" % (event.connection,))

    # Redirect HTML traffic
    url = "http://10.200.0.3/cassini/index.cgi"
    redirect_html(event,packet,url)
   
         
         
         
def redirect_html(event,packet,url):


    log.debug("Redirect HTTP traffic for mac: %s --> %s" % (packet.src, url))
    tcp_in = packet.find("tcp")
    # If HTTP traffic
    if tcp_in:
      if tcp_in.dstport == HTTP_PORT:     
       # if packet is a SYN packet, send a SYN/ACK
       if tcp_in.SYN == True:
         offset = 20 + len(tcp_in.options)
         send_tcp_syn_ack(event,packet)
       elif (tcp_in.ACK == True and tcp_in.PSH == False):
         return
         
       elif (tcp_in.ACK == True and  tcp_in.PSH == True):
         #print "Http request seen" 
         send_redirect(event,packet,url)
         send_tcp_reset(event,packet)
         
       return     
		
def send_tcp_syn_ack(event,packet):
      
      # Check if TCP 
      tcp_in = packet.find("tcp") 
      http_resp = pkt.tcp()
      payload = ""
       
      # Send HTTP response packet
      # Ethernet frame
      e = pkt.ethernet()
      e.src = packet.dst
      e.dst = packet.src
      e.type = e.IP_TYPE
       
      # Now create the IPv4 packet
      ipp = pkt.ipv4()
      ipp.protocol = ipp.TCP_PROTOCOL
       
      ipp.srcip = packet.find("ipv4").dstip
      ipp.dstip = packet.find("ipv4").srcip
      ipp.flags = packet.find("ipv4").flags

      http_resp.ACK = True
      http_resp.SYN = True
      http_resp.dstport = tcp_in.srcport
      http_resp.srcport = tcp_in.dstport
      http_resp.seq = gen_seq_num ()
      http_resp.ack = tcp_in.seq + 1
      http_resp.options = tcp_in.options
      http_resp.win = tcp_in.win
      http_resp.off = 10
        
	  # Hook them up...
      ipp.payload = http_resp
      e.payload = ipp
       
       
      # Send it back to the input port
      msg = of.ofp_packet_out()
      msg.actions.append(of.ofp_action_output(port = of.OFPP_IN_PORT))
      msg.data = e.pack()
       
      #print "Post pack"  
      #print  e.payload.payload
      msg.in_port = event.port
      event.connection.send(msg)         
         
def send_tcp_reset (event,packet): 

   # Check if TCP 
   tcp_in = packet.find("tcp")        
   
   
   #print "Send TCP Reset" 
   http_resp = pkt.tcp()
   payload = ""
       
   # Send HTTP response packet
   # Ethernet frame
   e = pkt.ethernet()
   e.src = packet.dst
   e.dst = packet.src
   e.type = e.IP_TYPE
       
   # Now create the IPv4 packet
   ipp = pkt.ipv4()
   ipp.protocol = ipp.TCP_PROTOCOL
       
   ipp.srcip = packet.find("ipv4").dstip
   ipp.dstip = packet.find("ipv4").srcip
   ipp.flags = packet.find("ipv4").flags
        
   http_resp.RST = True     
   http_resp.dstport = tcp_in.srcport
   http_resp.srcport = tcp_in.dstport
   http_resp.seq = tcp_in.ack 
   http_resp.ack = tcp_in.seq + len(tcp_in) + 24
   http_resp.options = tcp_in.options
   http_resp.off = 8
   http_resp.win = tcp_in.win
       
    
   # Hook them up...
   ipp.payload = http_resp
   e.payload = ipp
       
       
   # Send it back to the input port
   msg = of.ofp_packet_out()
   msg.actions.append(of.ofp_action_output(port = of.OFPP_IN_PORT))
   msg.data = e.pack()
   msg.in_port = event.port
   event.connection.send(msg)
   
   
   
def send_redirect (event,packet,url): 
  
   # Check if TCP 
   tcp_in = packet.find("tcp")        
   
   
   #print "Send TCP Reset" 
   http_resp = pkt.tcp()
   payload = ""
       
   # Send HTTP response packet
   # Ethernet frame
   e = pkt.ethernet()
   e.src = packet.dst
   e.dst = packet.src
   e.type = e.IP_TYPE
       
   # Now create the IPv4 packet
   ipp = pkt.ipv4()
   ipp.protocol = ipp.TCP_PROTOCOL
       
   ipp.srcip = packet.find("ipv4").dstip
   ipp.dstip = packet.find("ipv4").srcip
   ipp.flags = packet.find("ipv4").flags
   
   # Now that we are established respond to any request with a redirect
   http_resp.ACK = True
   http_resp.PSH = True
   http_resp.dstport = tcp_in.srcport
   http_resp.srcport = tcp_in.dstport
   http_resp.seq = tcp_in.ack 
   http_resp.ack = tcp_in.seq + len(tcp_in) + 24
   http_resp.options = tcp_in.options
   http_resp.off = 8
   http_resp.win = tcp_in.win
   # Add mac and ip to url
   url_f = url + "?mac=" +  str(e.dst) + "&ip=" + str(ipp.dstip)  
   http_resp.payload = get_redirect_payload(url_f)
         
   #print "GET total size %d" % len(tcp_in)
   #print "GET payload size %d" % len(tcp_in.payload)
   # Hook them up...
   ipp.payload = http_resp
   e.payload = ipp
       
       
   # Send it back to the input port
   msg = of.ofp_packet_out()
   msg.actions.append(of.ofp_action_output(port = of.OFPP_IN_PORT))
   msg.data = e.pack()
   msg.in_port = event.port
   event.connection.send(msg)
         

     
   

def get_redirect_payload (url):

    captive_portal_url = url 

    # Get current time in RFC 1123 format
    now = datetime.now()
    stamp = mktime(now.timetuple())
    http_now = format_date_time(stamp)
      
    redirect_payload = "<HTML><HEAD><meta http-equiv=\"content-type\" " \
      "content=\"text/html;charset=utf-8\">" \
      "<TITLE>Redirect to Captive Portal</TITLE></HEAD><BODY>Redirect to Captive Portal</BODY></HTML>\n"  
      
    payload_len = len(redirect_payload) 
    
    redirect_hdr = "HTTP/1.1 302 Found\r\n" \
      "Location: %s\r\n" \
      "Cache-Control: no-cache\r\n" \
      "Content-Type: text/html; charset=UTF-8\r\n" \
      "Server: Cassini\r\n" \
      "Content-Length: %d\r\n" \
      "Date: %s\r\n\r\n" % (captive_portal_url, payload_len, http_now)
     
    redirect_str =  redirect_hdr + redirect_payload
    return redirect_str



   
   
   
def gen_seq_num ():

   seq_num = os.urandom(4).encode('hex')   
   return int(seq_num,16)

def launch (transparent=False):
  """
  Starts the NAC process 

  """ 
  core.registerNew(HttpRedirect, str_to_bool(transparent))
  