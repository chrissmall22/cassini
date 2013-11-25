from sqlalchemy import orm
import datetime
from sqlalchemy import schema, types

metadata = schema.MetaData()

def now():
    return datetime.datetime.now()


mac_table = schema.Table('nac_mactable', metadata,
  schema.Column('id', types.Integer, primary_key=True),
  schema.Column('mac', types.String(32)),
  schema.Column('ip', types.String(64)),
  schema.Column('state', types.String(64)),
  schema.Column('user_id', types.String(32)),
  schema.Column('dpid', types.String(32)),
  schema.Column('port', types.Integer),
  )

switch = schema.Table('switch', metadata,
  schema.Column('id', types.Integer, primary_key=True),
  schema.Column('dpid', types.String(32)),
  schema.Column('name', types.String(128)),
  schema.Column('os', types.String(128)),
  )

link = schema.Table('link', metadata,
  schema.Column('id', types.Integer, primary_key=True),
  schema.Column('a_dpid', types.String(32)),       
  schema.Column('z_dpid', types.String(32)),
  schema.Column('a_port', types.Integer), 
  schema.Column('z_port', types.Integer),
  )


class NAC_MacTable(object):
    pass

class Switch(object):
    pass

class Link(object):
    pass

orm.mapper(NAC_MacTable, mac_table)
orm.mapper(Switch, switch)
orm.mapper(Link, link)
