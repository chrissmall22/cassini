# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.db import models

class Link(models.Model):
    id = models.IntegerField(primary_key=True)
    a_dpid = models.CharField(max_length=32L, blank=True)
    z_dpid = models.CharField(max_length=32L, blank=True)
    a_port = models.IntegerField(null=True, blank=True)
    z_port = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'link'

class NacMactable(models.Model):
    id = models.IntegerField(primary_key=True)
    mac = models.CharField(max_length=32L, blank=True)
    ip = models.CharField(max_length=64L, blank=True)
    state = models.CharField(max_length=64L, blank=True)
    user_id = models.CharField(max_length=32L, blank=True)
    dpid = models.CharField(max_length=32L, blank=True)
    port = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'nac_mactable'

    def __unicode__(self):
   	return unicode(self.mac) or u''

class Users(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.CharField(max_length=32L, blank=True)
    real_name = models.CharField(max_length=64L, blank=True)
    class Meta:
        db_table = 'users'

class Networks(models.Model):
    id = models.IntegerField(primary_key=True)
    net_name = models.CharField(max_length=32L, blank=True)
    

class Applications(models.Model):
    id = models.IntegerField(primary_key=True)
    app_name = models.CharField(max_length=32L, blank=True)
    app_desc = models.CharField(max_length=128L, blank=True)
    params = models.CharField(max_length=128L, blank=True) 
    
    

class Switch(models.Model):
    id = models.IntegerField(primary_key=True)
    dpid = models.CharField(max_length=32L, blank=True)
    name = models.CharField(max_length=128L, blank=True)
    os = models.CharField(max_length=128L, blank=True)
    class Meta:
        db_table = 'switch'
    def __str__(self): 
        return str(self.name) + "dpid :" + str(self.dpid)
