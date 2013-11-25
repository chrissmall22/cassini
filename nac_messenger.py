from pox.core import core
from pox.messenger import *
import time
from pox.lib.recoco import Timer

log = core.getLogger()

class NAC_Messenger (object):
   def __init__ (self):
      nac_channel = core.MessengerNexus.get_channel("nac")
      def handle_chat (event, msg):
        print "handle_chat"
        m = str(msg.get("msg"))
        nac_channel.send({"msg":str(event.con) + " says " + m})
      nac_channel.addListener(MessageReceived, handle_chat)
      
      core.MessengerNexus.default_bot.add_bot(GreetBot)

class GreetBot (ChannelBot):
  def _join (self, event, connection, msg):
    print "==Greet Bot ==="
    print connection
    from random import choice
    greet = choice(['hello','aloha','greeings','hi',"g'day"])
    greet += ", " + str(connection)
    self.send({'greeting':greet})
    
def launch ():
  NAC_Messenger() 
  
  
  
     
 
