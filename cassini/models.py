from django.db import models

# Create your models here.

class MacDB(models.Model):
    mac = models.CharField(max_length=12)
    ip = models.GenericIPAddressField()
    os = models.CharField(max_length=64)
    fqdn = models.CharField(max_length=128)
    dpid = models.CharField(max_length=16)
    port = models.IntegerField()
    
    def __unicode__(self):
        return self.mac


class Nac_state(models.Model):
    mac = models.ForeignKey(MacDB) 
    state = models.CharField(max_length=16)
    user = models.CharField(max_length=16)
    
    def __unicode__(self):
        return u'%s %s %s' % (self.mac, self.state, self.user)

class Nac_network(models.Model):
    portal_url = models.URLField()
    quar_url = models.URLField()
    network = models.ForeignKey(Network)
    
    def __unicode__(self):
        return u'%s %s %s' % (self.network, self.portal_url, self.quar_url)
    
    
class Network(models.Model):
	name = models.CharField(max_length=32)
    desc = models.CharField(max_length=128)
    
    def __unicode__(self):
        return u'%s %s' % (self.name, self.desc)
    
class Project(models.Model):
	name = models.CharField(max_length=64)   
    desc = models.CharField(max_length=128)
    
    def __unicode__(self):
        return u'%s %s' % (self.name, self.desc)
    
class User(models.Model):
	user_id = models.CharField(max_length=32)
	name = models.CharField(max_length=64)
	auth_type = models.CharField(max_length=16)
	project = models.ForeignKey(Project)
    
    def __unicode__(self):
        return u'%s %s %s' % (self.user_id, self.name, self.auth_type)


