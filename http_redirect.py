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
   
         
         
         
def redirect_html(event,packet,url,rnum):

    #print "== redirect # %d" % (rnum)

    log.debug("Redirect HTTP traffic for mac: %s --> %s" % (packet.src, url))
    tcp_in = packet.find("tcp")
    # If HTTP traffic
    if tcp_in:
      if tcp_in.dstport == HTTP_PORT:     
       # if packet is a SYN packet, send a SYN/ACK
       if (tcp_in.SYN == True and tcp_in.ACK == False):
         offset = 20 + len(tcp_in.options)
         send_tcp_syn_ack(event,packet)
         print "== SYN/ACK"
         return "SYN"
       # if TCP is established
       elif (tcp_in.ACK == True and tcp_in.PSH == False and tcp_in.FIN == False and tcp_in.RST == False): 
         print "== Established ACK recieved : %d" % (rnum)
         estab_str = str(packet.find("ipv4").srcip) + ':' + str(tcp_in.srcport)
         #self.established[estab_str] = 1

         if rnum == 2:
           # ACK after redirect - lets close connection
           print " == TCP FIN"
           send_tcp_reset(event,packet)
           return "FIN"  
         else:   
           return "ESTABLISHED"


       elif (tcp_in.ACK == True and  tcp_in.PSH == True):
         # Check if we are established
         if rnum == 1: 
           # Lets check if this is a HTTP GET/POS
           request  = packet.raw[66:69]
           if (str(request) == 'GET' or str(request) == 'POS') :
             print "Http request seen %s : %d : %d request" % (request, packet.hdr_len,rnum)
             # Install path to portal
             push_portal_rule(event,packet.src)
             # Send HTTP redirect to portal
             send_redirect(event,packet,url)
             #print "== RESET"
             #send_tcp_reset(event,packet)
           else:
             print "== Non GET packet to HTTP"
           return "REDIRECT"
         else:  
           # ACK after redirect - lets close connection
           print " == TCP FIN"
           send_tcp_fin(event,packet)
           #send_tcp_reset(event,packet)
           return "FIN"  
       elif (tcp_in.ACK == True and tcp_in.FIN == True):
         print " === Recieved TCP FIN ACK =="
         # Close our side of the connection
         send_tcp_fin_ack(event,packet)
         rnum = 0
         return "CLOSED"
       elif (tcp_in.RST == True):
         print "== Reset recieved Connection closed"
         rnum = 0 
         #send_tcp_reset(event,packet)
         #denyflow(packet,event)
         return "CLOSED"    


def denyflow(flow, event):

  msg_drop = of.ofp_flow_mod()
  msg_drop.priority = 10
  msg_drop.match.dl_src = flow.src
  event.connection.send(msg_drop)
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
      http_resp.seq = tcp_in.seq
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

def send_tcp_fin_ack (event,packet): 

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
        
   #http_resp.FIN = True 
   http_resp.ACK = True     
           
   http_resp.dstport = tcp_in.srcport
   http_resp.srcport = tcp_in.dstport
   http_resp.seq = tcp_in.ack
   http_resp.ack = tcp_in.seq +1
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
         
def send_tcp_fin (event,packet): 

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
        
   http_resp.FIN = True     
   http_resp.dstport = tcp_in.srcport
   http_resp.srcport = tcp_in.dstport
   http_resp.seq = tcp_in.seq
   http_resp.ack = 0 
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
   
   # Now that we are established respond to any request with an ACK
   http_resp.ACK = True
   http_resp.dstport = tcp_in.srcport
   http_resp.srcport = tcp_in.dstport
   http_resp.seq = tcp_in.seq 
   # Needs to be seq_num + 
   http_resp.ack = tcp_in.seq + tcp_in.payload_len
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


   # Next lets send the HTTP redirect
   http_resp.PSH = True
   # ADD MAC AND IP TO URL
   url_f = url + "?mac=" + str(e.dst) + "&ip=" + str(ipp.dstip)
   http_resp.payload = get_redirect_payload(url_f)
         
   #PRINT "GET TOTAL SIZE %D" % LEN(TCP_IN)
   print "GET PAYLOAD SIZE %d" % tcp_in.payload_len
   # Hook them up...
   ipp.payload = http_resp
   e.payload = ipp
       
   # Send it back to the input port
   msg = of.ofp_packet_out()
   msg.actions.append(of.ofp_action_output(port = of.OFPP_IN_PORT))
   msg.data = e.pack()
   msg.in_port = event.port
   event.connection.send(msg)
         

def push_portal_rule (event,client_mac):

   HTTP_PORT = 80
   HTTPS_PORT = 443

   # Get all the trusted macs on the switch 
   
   #print "== Pushing trusted MACs into the flow table DPID: %s" % (event.dpid,)
   gw_mac_entry_list = get_mac_entry_state('PORT')
   client_mac_entry_list = get_mac_entry_list(client_mac)
   if not gw_mac_entry_list or not client_mac_entry_list:
     print "==No GW Found=="
     return  

   for gw_mac_entry in gw_mac_entry_list: 
     print "== HTTP IP %s " % (gw_mac_entry.ip,) 
     # To Portal Host -- 80
     msg_http = of.ofp_flow_mod()
     msg_http.match.dl_type = pkt.ethernet.IP_TYPE
     msg_http.match.nw_proto = pkt.ipv4.TCP_PROTOCOL
     msg_http.match.tp_dst = HTTP_PORT
     msg_http.priority = of.OFP_DEFAULT_PRIORITY + 10
     #msg_http.buffer_id = event.ofp.buffer_id
     if gw_mac_entry.ip:
       msg_http.match.nw_dst = IPAddr(gw_mac_entry.ip)
     # Send to Gateway MAC if on same SW as GW 
     if (int(gw_mac_entry.dpid) == event.dpid) and gw_mac_entry.port:
       msg_http.actions.append(of.ofp_action_output(port = gw_mac_entry.port))
     else:
       # If not on same SW push in NORMAL rule
       msg_http.actions.append(of.ofp_action_output(port = of.OFPP_NORMAL))    
     #event.connection.send(msg_http)
     # And port 443
     msg_http.match.tp_dst = HTTPS_PORT
     event.connection.send(msg_http)

     """
     # Now lets setup links to udc.u.washington.edu
     msg_http.match.nw_dst = IPAddr("173.250.227.13")
     event.connection.send(msg_http)
     msg_http.match.nw_dst = IPAddr("140.142.214.185")
     event.connection.send(msg_http)
     msg_http.match.nw_dst = IPAddr("128.95.155.179")
     event.connection.send(msg_http)

     # Now lets setup links to udc.u.washington.edu
     msg_http.match.nw_dst = IPAddr("173.250.227.27")
     event.connection.send(msg_http)
     msg_http.match.nw_dst = IPAddr("140.142.12.139")
     event.connection.send(msg_http)
     msg_http.match.nw_dst = IPAddr("128.95.155.207")
     event.connection.send(msg_http)
     msg_http.match.nw_dst = IPAddr("128.95.155.143")
     event.connection.send(msg_http)
     """
     


   for client_mac_entry in client_mac_entry_list: 
     # From Portal Host -- 80
     msg_http_ret = of.ofp_flow_mod()
     msg_http_ret.match.dl_type = pkt.ethernet.IP_TYPE
     msg_http_ret.match.nw_proto = pkt.ipv4.TCP_PROTOCOL
     msg_http_ret.match.tp_src = HTTP_PORT
     msg_http_ret.priority = of.OFP_DEFAULT_PRIORITY + 10
     #msg_http_ret.buffer_id = event.ofp.buffer_id
     msg_http_ret.match.dl_dst = EthAddr(client_mac_entry.mac)
     # Send to Client MAC if on same SW as Client
     if ((int(client_mac_entry.dpid) == event.dpid) and client_mac_entry.port):
       msg_http_ret.actions.append(of.ofp_action_output(port = event.port))
     else:
       # If not on same SW push in NORMAL rule
       msg_http_ret.actions.append(of.ofp_action_output(port = of.OFPP_NORMAL))
     #event.connection.send(msg_http_ret)
     # Send HTTPS
     msg_http_ret.match.tp_src = HTTPS_PORT
     event.connection.send(msg_http_ret)
      
     
   

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
  
