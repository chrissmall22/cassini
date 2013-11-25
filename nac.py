# Copyright 2013 Christopher Small

"""
Cassini - Network Access Control Application

A rewrite of the Resonance Network Access Control Application in PoX
Built to work with the Cassini Network Edge Manager 

While using some of the logic this is a rewrite with a DB and web interface view 
to be closly integrated

"""

from pox.core import core
from pox.messenger import *

import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt
from pox.lib.util import dpid_to_str
from pox.lib.util import str_to_bool
from pox.lib.addresses import IPAddr, EthAddr


from cassini.db import nac_db, model_orm
from cassini.db.nac_db import *
from cassini.http_redirect import redirect_html, push_trusted_macs

import socket

log = core.getLogger()


class NAC (object):
  """
  Waits for OpenFlow switches to connect.
  """
  
 
    
  def __init__ (self, connection, transparent):
    self.connection = connection
    self.transparent = transparent

    HTTP_PORT = 80
    HTTPS_PORT = 443


    # We want to hear PacketIn messages, so we listen
    # to the connection
    connection.addListeners(self)        
             
    
  def _handle_PacketIn (self, event):
    packet = event.parsed
    
    log.debug("PacketIn Connection %s" % (event.connection,))
    
    

    # Check if in the known MAC addresses, if so move host to last known state
    if get_mac_entry(packet.src):
      state = get_mac_entry(packet.src).state
    else: 
      state = 'REG'
      set_mac_entry(packet,event,state) 
    
    log.debug("Packet In, mac=%s DB state=%s",
              packet.src, state)
    
    # Check what state the host was in
    if state == 'OPER':
      # Push in normal rule     
      msg_oper = of.ofp_flow_mod() 
      msg_oper.match.dl_dst = packet.src
      msg_oper.actions.append(of.ofp_action_output(port = event.port))
      event.connection.send(msg_oper)
	
    if state == 'REG':
      #push_web_rules(packet.src,event)	
      url = "http://10.200.0.3/cassini/test.cgi"
      redirect_html(event,packet,url)
      #denyflow(packet,event)
     




def lookup(addr):
  try:
    return socket.gethostbyaddr(addr)
  except socket.herror:
    return None, None, None


def path_bfs(event,dst_mac):
  """
  Get list of ports to get a path to a mac from a packet in
  Uses Breadth First Search
  """
  # Get the location of the dst_mac
  dst_entry = get_mac_entry(dst_mac)
  dst_links = get_links_by_dpid(dst_entry.dpid)
  # BFS
  queue = [ ]
  print "==="
  print dst_links.a_dpid
  queue.append(dst_links)
  
  return 
  while queue:
    # Does dpid of queue 
    path = queue.pop(0)
    # get last node
    node = path[-1]
    # if node is src - path found
    if (node.a_dpid == event.dpid) or (node.z_dpid == event.dpid): 
       return path
    # enumerate all nodes at level
    links = get_links_by_dpid(node.a_dpid)
    for next_entries in links:
       new_path = list(path)
       new_path.append(next_entries)
       queue.append(new_path)
       

def push_default_rules (event):

   # Clear all existing rules
   msg_flush = of.ofp_flow_mod(command=of.OFPFC_DELETE)
   event.connection.send(msg_flush)

   # Push default rules so a host can DHCP
   # ARP 
   msg_arp = of.ofp_flow_mod()
   msg_arp.match.dl_type = pkt.ethernet.ARP_TYPE
   msg_arp.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
   event.connection.send(msg_arp)
   
   # DHCP 
   msg_dhcp = of.ofp_flow_mod()
   msg_dhcp.match.dl_type = pkt.ethernet.IP_TYPE
   msg_dhcp.match.nw_proto = pkt.ipv4.UDP_PROTOCOL
   msg_dhcp.match.tp_src = pkt.dhcp.CLIENT_PORT
   msg_dhcp.match.tp_dst = pkt.dhcp.SERVER_PORT
    	
   # Existing DHCPD server on network  -- client -> server
   msg_dhcp.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
   event.connection.send(msg_dhcp)
        
   # DHCP Server -> Client

   msg_dhcp.match.tp_src = pkt.dhcp.SERVER_PORT
   msg_dhcp.match.tp_dst = pkt.dhcp.CLIENT_PORT
        
   event.connection.send(msg_dhcp)
   
   

   
def denyflow(flow, event):

  msg_drop = of.ofp_flow_mod()
  msg_drop.match.dl_src = flow.src
  event.connection.send(msg_drop)
  return


""" 
 Handles multi - switch actions
"""

class nac (object):

  def __init__ (self, transparent):
    core.addListeners(self)
    self.transparent = transparent
    nac_channel = core.MessengerNexus.get_channel("nac")
    print " === NAC Channel ==="
    print nac_channel.name
    
    def handle_chat (event, msg):
      print "handle chat"
      m = str(msg.get("msg"))
      nac_channel.send({"msg":str(event.con) + " says " + m})
    nac_channel.addListener(MessageReceived, handle_chat) 

    

  def _handle_ConnectionUp (self, event):
    log.debug("Connection %s" % (event.connection,))
    NAC(event.connection, self.transparent)
    push_default_rules(event)
    push_trusted_macs(event)
    add_switch_db(event)

  def _handle_ConnectionDown (self, event):
    log.debug("Connection %s" % (event.connection,))
    del_switch_db(event)
       
    
      

def launch (transparent=False):
  """
  Starts the NAC process 

  """ 
  core.registerNew(nac, str_to_bool(transparent))
  