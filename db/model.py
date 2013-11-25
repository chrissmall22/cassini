from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()

class NAC_MacTable(Base):
  """"""
  __tablename__ = "nac_mactable"

  id = Column(Integer, primary_key=True)
  mac = Column(String(32))
  ip = Column(String(64))
  state = Column(String(64))
  user_id = Column(String(32))
  dpid = Column(String(32))
  port = Column(Integer)


class Switches(Base):
  """"""
  __tablename__ = "switches"

  id = Column(Integer, primary_key=True)
  dpid = Column(String(32))
  name = Column(String(128)) 
  os = Column(String(128))


class Links(Base):
  """"""
  __tablename__ = "links"

  id = Column(Integer, primary_key=True)
  a_dpid = Column(String(32))       
  z_dpid = Column(String(32))
  a_port = Column(Integer) 
  z_port = Column(Integer)



def init_sql(db):
   Base.metadata.create_all(db)
   
      
   