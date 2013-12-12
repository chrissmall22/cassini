#!/usr/bin/python

from cassini.db import nac_db, model_orm
from cassini.db.nac_db import session 


def get_mac_entry(mac):
	"""
	Given a MAC return db entry 
	"""
	
	mac_q = session.query(model_orm.NAC_MacTable).filter_by(mac=mac).all()
	if mac_q:
		return mac_q[0]
    

    		
def set_mac_entry():
  mac_entry = model_orm.NAC_MacTable()
  mac_entry.mac = '00:00:00:00:00:01'
  mac_entry.ip = '192.168.1.1'
  mac_entry.state = 'REG'
  mac_entry.dpid = '00-00-00-00-00-11'
  mac_entry.port = 1
  
  """
  foo = get_mac_entry(mac_entry.mac)
  if foo:
    print "========Test========"
    print  foo.mac, foo.ip, foo.state, foo.dpid, foo.port
  """
  
  mac_q = get_mac_entry(mac_entry.mac)
  if (not mac_q):
    session.add(mac_entry)
    session.flush()
    session.commit()
    
  return
  
def flush_all_macs():
    mac_q = session.query(model_orm.NAC_MacTable).all()
    for mac_entry in mac_q:
       session.delete(mac_q)        
    session.flush()
    session.commit()    

def flush_mac(mac):
    mac_q = session.query(model_orm.NAC_MacTable).filter_by(mac=mac).all()
    for mac_entry in mac_q:
       session.delete(mac_entry)        
    session.flush()
    session.commit()    	


test_addr = '00:00:00:00:00:01'
#flush_mac(test_addr)
set_mac_entry()
mac = get_mac_entry(test_addr)
print  mac.mac, mac.ip


		

