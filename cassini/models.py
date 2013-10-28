from django.db import models

# Create your models here.

class MacDB(models.Model):
    mac = models.CharField(max_length=12)
    #ip = models.GenericIPAddressField(null=True)
    #os = models.CharField(max_length=64, null=True, blank=True)
    #fqdn = models.CharField(max_length=128, null=True)
    dpid = models.CharField(max_length=16)
    port = models.IntegerField()
    
    def __unicode__(self):
        return self.mac

class Network(models.Model):
	name = models.CharField(max_length=32)
	desc = models.CharField(max_length=128, null=True)
	
	def __unicode__(self):
	  return u'%s %s' % (self.name, self.desc)
    
class Project(models.Model):
	name = models.CharField(max_length=64)
	desc = models.CharField(max_length=128,null=True)
	
	def __unicode__(self):
	  return u'%s %s' % (self.name, self.desc)
    
class User(models.Model):
	user_id = models.CharField(max_length=32)
	name = models.CharField(max_length=64,null=True )
	auth_type = models.CharField(max_length=16, null=True)
	project = models.ManyToManyField(Project)
	
	def __unicode__(self):
	  return u'%s %s %s' % (self.user_id, self.name, self.auth_type)
	  
	  
# Classes Specific to the NAC application -- should be split out	  

class Nac_state(models.Model):
    mac = models.ForeignKey(MacDB) 
    state = models.CharField(max_length=16)
    user = models.ForeignKey(User)
    
    def __unicode__(self):
        return u'%s %s %s' % (self.mac, self.state, self.user)

class Nac_network(models.Model):
    portal_url = models.URLField()
    quar_url = models.URLField()
    network = models.ForeignKey(Network)
    
    def __unicode__(self):
        return u'%s %s %s' % (self.network, self.portal_url, self.quar_url)
        
	


