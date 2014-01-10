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
from cassini.http_redirect import redirect_html

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
    
    self.num_redirect = 0 
  
    self.established = {}

    # We want to hear PacketIn messages, so we listen
    # to the connection
    connection.addListeners(self)        
   
  def _handle_ConnectionUp (self, event):
    log.debug("Connection %s" % (event.connection,))
    # Allow ARP and DHCP everywhere
    push_default_rules(event)
    # push trusted hosts
    push_trusted_hosts(event)
    # Allow Shib IPs
    push_shib(event)
    # Register Switch in the DB
    add_switch_db(event)        
    
  def _handle_PacketIn (self, event):
    packet = event.parsed
    
    log.debug("PacketIn Connection %s" % (event.connection,))
    
    # Check if in the known MAC addresses, if so move host to last known state
    if get_mac_entry(packet.src):
      state = get_mac_entry(packet.src).state
      #print "== DB State %s ==" % (state,)
    else: 
      state = 'REG'
      set_mac_entry(packet,event,state) 
    
    log.debug("Packet In, mac=%s DB state=%s",
              packet.src, state)
    #print "=PI= mac=%s  state=%s db_state=%s" % ( packet.src, state, get_mac_entry(packet.src).state ) 
    # Check what state the host was in
    if state == 'OPER':
      print "==OPER"      # Push in normal rule     
      push_normal(packet.src,event)
  	
    if state == 'REG':
      # if packet is DNS
      tcp_in = packet.find("tcp")
      if packet.find("dns"):
        #print "== DNS Packet port %s ==" % (event.port,)
        push_dns_rule(event,packet.src)
        #set_host_ip(mac,ip)  
        #print "== DNS Done =="
        
      # Check Packet is HTTP and redirect
      elif tcp_in:
        #print "==TCP"
        if tcp_in.dstport == 80:
           #print "== HTTP Packet port %s ==" % (event.port,)
           #push_portal_rule(event,packet.src)
           print "== HTTP Packet redirect_html == %d %s : %d" % (self.num_redirect,str(packet.find("ipv4").srcip),tcp_in.srcport)
           src_estab = str(packet.find("ipv4").srcip) + ':' + str(tcp_in.srcport)
           rnum = 0
           print self.established
           if src_estab in self.established:
             print "foo: %s" % (src_estab)
             if self.established[src_estab] == "ESTABLISHED":
               rnum = 1
             elif self.established[src_estab] == "REDIRECT":
               rnum = 2
             else: 
               rnum = 0
           ret = redirect_html(event,packet,'https://puppet.cac.washington.edu/cassini/index.cgi',rnum)
           self.established[src_estab] = ret
           print "============ %s %s %d" % (src_estab,ret, rnum)
           #push_portal_rule(event,packet.src)
           
           
    if state == 'AUTH':
      print "==AUTH"
      # This is a NOP for now but could put a scanner test here
      set_mac_entry_state(packet.src,'OPER')
      # Remove all rules based on client mac
      #remove_rules(packet.src,event)
      # Push in normal rule     
      push_normal(packet.src,event)


"""
Push rule to send DNS packet to GW/DNS Server
"""

def push_dns_rule (event,client_mac):

  DNS_PORT = 53  

  gw_mac_entry = get_mac_entry_state('PORT')
  client_mac_entry_list = get_mac_entry_list(client_mac)
  if not gw_mac_entry or not client_mac_entry_list:
     print "==No GW Found=="
     return

  for gw_entry in gw_mac_entry:
    print "==DNS rule add %s (mac: %s) -> port %s" % (gw_entry.ip,gw_entry.mac,gw_entry.port)
    # To GW/DNS Host -- 53
    msg_dns = of.ofp_flow_mod()
    msg_dns.match.dl_type = pkt.ethernet.IP_TYPE
    msg_dns.match.nw_proto = pkt.ipv4.UDP_PROTOCOL
    msg_dns.match.tp_dst = DNS_PORT
    msg_dns.priority = of.OFP_DEFAULT_PRIORITY + 10
    msg_dns.buffer_id = event.ofp.buffer_id

    if gw_entry.mac:
       msg_dns.match.dl_dst = EthAddr(gw_entry.mac) 
    # Send to Gateway MAC if on same SW as GW
    print "==DPIDS db: %s event: %s %s" % (gw_entry.dpid, event.dpid, gw_entry.mac)
    if ((int(gw_entry.dpid) == event.dpid) and gw_entry.port):
      msg_dns.actions.append(of.ofp_action_output(port = gw_entry.port))
    else:
      #print "==Normal=="
      # If not on same SW push in NORMAL rule
      msg_dns.actions.append(of.ofp_action_output(port = of.OFPP_NORMAL))
    #print msg_dns
    event.connection.send(msg_dns)  
  
  for client_mac_entry in client_mac_entry_list:
    print client_mac_entry.mac
    # From GW/DNS Host -- 53
    print "==DNS rule RET add (mac: %s) port %s" % (client_mac_entry.mac,event.port)
    msg_dns_ret = of.ofp_flow_mod()
    msg_dns_ret.match.dl_type = pkt.ethernet.IP_TYPE
    msg_dns_ret.match.nw_proto = pkt.ipv4.UDP_PROTOCOL
    msg_dns_ret.match.tp_src = DNS_PORT
    msg_dns_ret.priority = of.OFP_DEFAULT_PRIORITY + 10
    #msg_dns_ret.buffer_id = event.ofp.buffer_id
    
    msg_dns_ret.match.dl_dst = EthAddr(client_mac_entry.mac)
    # Send to Client MAC if on same SW as Client
    if int(client_mac_entry.dpid) == event.dpid and client_mac_entry.port:
       print "== DNS RET port %d" % (event.port,)
       msg_dns_ret.actions.append(of.ofp_action_output(port = event.port))
    else:
      # If not on same SW push in NORMAL rule
      print "==Normal=="
      msg_dns_ret.actions.append(of.ofp_action_output(port = of.OFPP_NORMAL))
    #print msg_dns_ret
    event.connection.send(msg_dns_ret)
  

    
    


"""
Given mac address allow connections to it
"""
def push_normal(mac,event):

  # Delete all existing Rules about mac

  msg_del = of.ofp_flow_mod() 
  msg_del.match.dl_src = mac
  msg_del.actions.append(of.ofp_action_output(port = of.OFPFC_DELETE))
  event.connection.send(msg_del)
  
  msg_del2 = of.ofp_flow_mod() 
  msg_del2.match.dl_dst = mac
  msg_del2.actions.append(of.ofp_action_output(port = of.OFPFC_DELETE))
  event.connection.send(msg_del2)
  
  msg_oper = of.ofp_flow_mod() 
  msg_oper.match.dl_src = mac
  msg_oper.actions.append(of.ofp_action_output(port = of.OFPP_NORMAL))
  event.connection.send(msg_oper)

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


   # Push all DNS and HTTP to contriller to set up paths to portal and dns server
   # Port 80 to controller
   msg_http = of.ofp_flow_mod()
   msg_http.match.dl_type = pkt.ethernet.IP_TYPE
   msg_http.match.nw_proto = pkt.ipv4.TCP_PROTOCOL
   msg_http.match.tp_dst = 80
   #msg_http.priority = of.OFP_DEFAULT_PRIORITY - 10
   msg_http.actions.append(of.ofp_action_output(port = of.OFPP_CONTROLLER))
   #event.connection.send(msg_http)
   
   # Push all DNS and HTTP to contriller to set up paths to portal and dns server

   # Push path to idp.u.washington.edu
   # Should get this from DNS not hardcoded
   


   # Drop everything except for the DNS and HTTP
   msg_drop = of.ofp_flow_mod()
   msg_drop.priority = of.OFP_DEFAULT_PRIORITY - 10
   #event.connection.send(msg_drop)
   


def push_shib (event):

     msg_http = of.ofp_flow_mod()
     msg_http.match.dl_type = pkt.ethernet.IP_TYPE
     msg_http.match.nw_proto = pkt.ipv4.TCP_PROTOCOL
     msg_http.match.tp_dst = 443
     msg_http.priority = of.OFP_DEFAULT_PRIORITY + 10
     #msg_http.buffer_id = event.ofp.buffer_id
           
     msg_http.actions.append(of.ofp_action_output(port = 5))
    
           
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

     msg_http.match.nw_dst = IPAddr("128.208.125.59")
     event.connection.send(msg_http)

     # CA
     msg_http.match.tp_dst = 80
     msg_http.match.nw_dst = IPAddr("178.255.83.1")
     event.connection.send(msg_http)

   

 
def push_trusted_hosts (event):

   # Get all the trusted macs on the switch 
   #print "== Pushing trusted MACs into the flow table DPID: %s" % (event.dpid,)
   mac_entry_list = get_mac_entry_state('PORT')
   for mac_entry in mac_entry_list:
     db_dpid = int(mac_entry.dpid)
     #print "Trusted2 MAC %s %d db: %d" % (mac_entry.mac,event.dpid,db_dpid) 
     if event.dpid == db_dpid:
       #print "Trusted MAC %s" % (mac_entry.mac,) 
       # To Portal Host 
       msg_trust = of.ofp_flow_mod()
       msg_trust.match.dl_src = EthAddr(mac_entry.mac)
       msg_trust.actions.append(of.ofp_action_output(port = of.OFPP_NORMAL))
       event.connection.send(msg_trust)
       
       
   
   return  

   
def denyflow(flow, event):

  msg_drop = of.ofp_flow_mod()
  msg_drop.priority = 10
  msg_drop.match.dl_src = flow.src
  event.connection.send(msg_drop)
  return


""" 
 Handles multi - switch actions
"""

class nac_multi (object):

  def __init__ (self, transparent):
    core.openflow.addListeners(self)
    self.transparent = transparent
    nac_channel = core.MessengerNexus.get_channel("nac")
    
    # Set MAC to AUTH if authenticated
    def handle_nac_auth (event, msg):
      mac = str(msg.get("mac"))
      ip = str(msg.get("ip"))
      user = str(msg.get("user"))
      state = str(msg.get("state"))
      log.debug("==Auth msg == mac:%s ip:%s user:%s" % (mac,ip,user))
      # Validate
      if (state == 'AUTH' or state == 'REG' or state == 'TRUS'): 
        set_mac_entry_state(mac,state) 
        set_mac_entry_user(mac,user)
                      
    nac_channel.addListener(MessageReceived, handle_nac_auth) 

    
  def _handle_ConnectionUp (self, event):
    log.debug("Connection %s" % (event.connection,))
    #print "======NAC"
    NAC(event.connection, self.transparent)



  def _handle_ConnectionDown (self, event):
    log.debug("Connection %s" % (event.connection,))
    del_switch_db(event)
       
    
      

def launch (transparent=False):
  """
  Starts the NAC process 

  """ 
  core.registerNew(nac_multi, str_to_bool(transparent))
  
