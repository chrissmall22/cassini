from django.template.loader import get_template
from django.template import Template, Context
from django.http import HttpResponse

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.core import serializers

from cassini.models import Switch, NacMactable


import datetime
import json

def hello(request):
    return HttpResponse("Hello world")

def overview(request):
    stats = get_stats()
    t = get_template('overview.html')
    html = t.render(Context(stats))
    return HttpResponse(html)


def switches(request):
    now = datetime.datetime.now()
    t = get_template('switches.html')
    sw_table = Switch.objects.all() 
    html = t.render(Context({'sw_table': sw_table}))
    return HttpResponse(html)

def hosts(request):
    now = datetime.datetime.now()
    t = get_template('hosts_ajax.html')
    mactable_list = NacMactable.objects.all()
    html = t.render(Context({'mac_table': mactable_list})) 
    return HttpResponse(html)

def users(request):
    now = datetime.datetime.now()
    t = get_template('users.html')
    mactable_list = NacMactable.objects.all()
    html = t.render(Context({'maclist': mactable_list}))
    return HttpResponse(html)

def networks(request):
    now = datetime.datetime.now()
    t = get_template('networks.html')
    mac_table = NacMactable.objects.all()
    html = t.render(Context({'mac_table': mac_table}))
    return HttpResponse(html)



def about(request):
    t = get_template('about.html')
    html = t.render(Context())
    return HttpResponse(html)

def contact(request):
    t = get_template('contact.html')
    html = t.render(Context())
    return HttpResponse(html)

def placeholder(request):
    t = get_template('placeholder.html')
    html = t.render(Context())
    return HttpResponse(html)

def login(request):
    t = get_template('login_text.html')
    html = t.render(Context())
    return HttpResponse(html)


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect("/foo/")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {
        'form': form,
    })


def update_db(request):


   mac = "00:00:00:00:00:01"
   state = "REG"

   if request.method == 'POST':
    
      mac = request.POST['mac']
      state = request.POST['state']
      mac_table = NacMactable.objects.filter(mac=mac)
      mac_table.state = state

      mac_table.save()

   t = get_template('about.html')
   html = t.render(Context({'mac': mac, 'state': state}))

   return HttpResponse(html)

  

def ajax(request):
  
    dt = {} 
    mac_table = NacMactable.objects.all()
   
    #dt['aaData'] = mac_table
    #for mac in mac_table:
    #foo = foo + serializers.serialize("json",mac_entry)
    #foo = foo + serializers.serialize("json",mac_table)
    #foo = foo + "{ " + serializers.serialize("json",mac) +  " },"
    #foo = foo + "{ \"mac\": \"" + mac.mac + "\", \"ip\": \"" + mac.ip + "\", \"dpid\": \"" + str(mac.dpid) + "\", \"port\": \"" + str(mac.port) + "\", \"user_id\": \"" + mac.user_id + "\" },"
    #foo = foo + "{ \"mac\": \"" + mac.mac + "\" , \"ip\": \"" + mac.ip + "\" },\n"	
    #foo = foo + "\n } "

    table = set_buttons(mac_table)
    
    mac_table_json = serializers.serialize("json",table)
    
    final_json = "{ \"aaData\": \n" + mac_table_json + "\n }"

    return HttpResponse(final_json,'json')

# Functions


def set_buttons(table):

   states = [ "Registration", "Authenticated", "Operational", "Gateway", "Quarantine" ] 

   for mac_entry in table:
     if mac_entry.state == 'REG': 
        state_name  = "Registration"
        button_style = "btn-primary"
     elif mac_entry.state == 'AUTH': 
        state_name  = "Authenticated"
        button_style = "btn-warning"
     elif mac_entry.state == 'OPER': 
        state_name  = "Operational"
        button_style = "btn-success"
     elif mac_entry.state == 'QUAR': 
        state_name  = "Quarantine"
        button_style = "btn-critical" 
     elif mac_entry.state == 'PORT':
        state_name  = "Gateway"
        button_style = "btn-success"
     else:
        state_name  = mac_entry.state 
        button_style = "btn-warning"


     button_str = "<div class=\"btn-group\"> <button type=\"button\" data-toggle=\"dropdown\" class=\"btn dropdown-toggle " + button_style + "\">" + state_name + "<span class=\"caret\"></span> </button> <ul class=\"dropdown-menu\" role=\"menu\">"

     for state in states:
        update_str = "'" + state + "','" + mac_entry.mac + "'"
	update_str = "'REG','" + mac_entry.mac + "'"
        button_str += "<li><a href=\"\" onclick=\"post_to_url('/cassini/updatedb'," + update_str + ")\">" + state + "</a></li>"
     button_str += "</ul></div>"
     mac_entry.state = button_str 

  
   return table

def get_stats():
    now = datetime.datetime.now()
    # Need to do active
    tot_sw = Switch.objects.count()
    tot_hosts = NacMactable.objects.count()
    users = NacMactable.objects.values('user_id').distinct()
    tot_users =  users.count()

      
    stats = { 'current_date': now,
		 'tot_switches': tot_sw,
                 'tot_hosts': tot_hosts,
                 'tot_users': tot_users  }
    return stats
