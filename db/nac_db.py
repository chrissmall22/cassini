import model_orm
from sqlalchemy import orm
from sqlalchemy import create_engine
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt
from pox.lib.util import dpid_to_str
from pox.lib.util import str_to_bool
from pox.lib.addresses import IPAddr, EthAddr


# Create an engine and create all the tables we need
engine = create_engine('mysql://root:rise56stop@localhost/test_cassini', echo=False)
#engine = create_engine('sqlite:///:memory:', echo=True)
model_orm.metadata.bind = engine
model_orm.metadata.create_all()

# Set up the session
sm = orm.sessionmaker(bind=engine, autoflush=True, autocommit=False,
    expire_on_commit=True)
session = orm.scoped_session(sm)

def set_link(link):

  link_entry = model_orm.Link()
  link_entry.a_dpid = link.dpid1
  link_entry.z_dpid = link.dpid2
  link_entry.a_port = link.port1
  link_entry.z_port = link.port2

  link_q = get_link(link)
  if (not link_q):
    # Add to database 
    session.add(link_entry)
    session.flush()
    session.commit()

def get_links_by_dpid(dpid):
   links = []
   # Given a dpid
   link_q1 = session.query(model_orm.Link).filter_by(a_dpid=dpid).all()
   for link_q1_entity in link_q1:
       links.append(link_q1_entity)
   link_q2 = session.query(model_orm.Link).filter_by(z_dpid=dpid).all()
   for link_q2_entity in link_q2:
       links.append(link_q2_entity)   
   return links 
    
       
def get_link(link):
   # Check if link exists
   link_q1 = session.query(model_orm.Link).filter_by(a_dpid=link.dpid1,z_dpid=link.dpid2,a_port=link.port1,z_port=link.port2).all() 
   for link_q1_entity in link_q1:
		return link_q1_entity
   # Check the reverse link	
   link_q2 = session.query(model_orm.Link).filter_by(a_dpid=link.dpid2,z_dpid=link.dpid1,a_port=link.port2,z_port=link.port1).all() 
   for link_q2_entity in link_q2:
		return link_q2_entity	
   return	        
  
def del_link(link):
   # Check if link exists
   link_q1 = session.query(model_orm.Link).filter_by(a_dpid=link.dpid1,z_dpid=link.dpid2,a_port=link.port1,z_port=link.port2).all() 
   for link_q1_entity in link_q1:
	 session.delete(link_q1_entity)
   # Check the reverse link	
   link_q2 = session.query(model_orm.Link).filter_by(a_dpid=link.dpid2,z_dpid=link.dpid1,a_port=link.port2,z_port=link.port1).all() 
   for link_q2_entity in link_q2:
     session.delete(link_q2_entity)
     session.flush()
     session.commit()  
  
  
def add_switch_db(event):
  """
  Enter switch into the DB
  """
  
  switch = model_orm.Switch()
  switch.dpid = event.dpid
  """
  # TODO: set IP of switch 
  switch.ip = event.ip
  sw_name = lookup(switch.ip)
  if sw_name:
     switch.name = sw_name
  # TODO: Get other data about switch through OpenFlow proto or snmp
  """
  switch.os = 'Unknown'
  
  # Check if switch with same DPID already exists
  sw = get_switch_db(event.dpid)
  if (not sw):
    # Add to database 
    session.add(switch)
    session.flush()
    session.commit()

def get_switch_db(dpid):
  switch_q = session.query(model_orm.Switch).filter_by(dpid=dpid).all()
  if switch_q:
    return switch_q[0]
	


def del_switch_db(event):
    switch_q = session.query(model_orm.Switch).filter_by(dpid=event.dpid).all()
    for switch in switch_q:
       session.delete(switch)        
    session.flush()
    session.commit()  



def set_mac_entry(packet,event,state):
  """
  Enter mac into the DB
  """
  mac_entry = model_orm.NAC_MacTable()
  mac_entry.mac = packet.src
  # If IP set src address in table 
  # mac_entry.ip = '127.0.0.1'
  mac_entry.state = state
  mac_entry.dpid = event.dpid
  mac_entry.port = event.port
  
  
  mac_q = get_mac_entry(mac_entry.mac)
  if (not mac_q):
    session.add(mac_entry)
    session.flush()
    session.commit()
    
  return


def set_mac_entry_state(mac,state):
    
    print "==SET MES== %s %s" % (mac, state)  
    session.query(model_orm.NAC_MacTable).filter_by(mac=mac).update({"state": state})
    session.flush()
    session.commit()
     
    return


# Get all the switches in "X" state
def get_mac_entry_state(state):
        
  mac_q = session.query(model_orm.NAC_MacTable).filter_by(state=state).all()
  if mac_q:
    return mac_q



def get_mac_entry(mac):
        
  mac_q = session.query(model_orm.NAC_MacTable).filter_by(mac=mac).all()
  if mac_q:
    return mac_q[0]


def get_portal_ip():	
  # Get Web Portal IP
  webportal_ip = '10.200.0.3'	 
  return webportal_ip

def get_portal_mac():
  # Get Web Portal IP
  webportal_mac = '00:00:00:00:00:03'
  return webportal_mac   


"""
   # Put in a rule to bypass all all V6 Traffic 
   msg_v6 = of.ofp_flow_mod()
   msg_v6.match.dl_type = pkt.ethernet.IPV6_TYPE
   msg_v6.actions.append(of.ofp_action_output(port = of.OFPP_NORMAL))
   event.connection.send(msg_v6)
"""     