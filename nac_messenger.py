from pox.core import core
from pox.messenger import *
import time
from pox.lib.recoco import Timer

log = core.getLogger()

class NAC_Messenger (object):
   def __init__ (self):
      nac_channel = core.MessengerNexus.get_channel("nac")
      
      def handle_nac_auth (event, msg):
        mac = str(msg.get("mac"))
        ip = str(msg.get("ip"))
        user = str(msg.get("user"))
        print "==Auth msg == mac:%s ip:%s user:%s" % (mac,ip,user)
       
      nac_channel.addListener(MessageReceived, handle_nac_auth)
      
    
def launch ():
  NAC_Messenger() 
  
  
  
     
 
