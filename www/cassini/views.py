from django.template.loader import get_template
from django.template import Template, Context, RequestContext
from django.http import HttpResponse

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.core import serializers

from cassini.models import Switch, NacMactable, Projects


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
    t = get_template('switches_ajax.html')
    html = t.render(Context())
    return HttpResponse(html)

def hosts(request):
    now = datetime.datetime.now()
    t = get_template('hosts_ajax.html')
    mactable_list = NacMactable.objects.all()
    html = t.render(Context({'mac_table': mactable_list})) 
    return HttpResponse(html)

def users(request):
    now = datetime.datetime.now()
    t = get_template('users_ajax.html')
    html = t.render(Context())
    return HttpResponse(html)


def projects(request):
    t = get_template('projects_ajax.html')
    html = t.render(Context())
    return HttpResponse(html)

def networks(request):
    now = datetime.datetime.now()
    t = get_template('networks.html')
    mac_table = NacMactable.objects.all()
    html = t.render(Context({'mac_table': mac_table}))
    return HttpResponse(html)

def apps(request):
    t = get_template('apps.html')
    html = t.render(Context())
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

   if request.method == 'GET':
    
     state = request.GET['state']
     mac = request.GET['mac']
     mac_table = NacMactable.objects.get(mac=mac)
     mac_table.state = state
     mac_table.save()

   t = get_template('update.html')
   html = t.render(Context({'mac': mac, 'state': state}))

   return HttpResponse(html)


def ajax_projects(request):

    proj_table = Projects.objects.all()
    
    for proj in proj_table:
        if proj.status:
           proj.status = "Active"
        else: 
	   proj.status = "Unconnected"
        if proj.admin_status:
           proj.admin_status = set_proj_button(proj.admin_status)
	   
    proj_json = serializers.serialize("json",proj_table)
    final_json = mk_aaData(proj_json)
    return HttpResponse(final_json,'json')


def set_proj_button(status):
    if status:
      str = "<div class=\"cassini_button cassini_button_active\">Disable</div>"
    else: 
      str = "<div class=\"cassini_button cassini_button_disable\">Activate</div>"

    return str

def ajax_hosts(request):
  
    dt = {} 
    mac_table = NacMactable.objects.all()
    table = set_buttons(mac_table)
    mac_table_json = serializers.serialize("json",table)
    final_json = "{ \"aaData\": \n" + mac_table_json + "\n }"
    return HttpResponse(final_json,'json')

def ajax_switches(request):

    switches = Switch.objects.all()
    for switch in switches:
       switch.status = switch_button(switch.status)

    switches_json = serializers.serialize("json",switches)
    final_json = mk_aaData(switches_json) 

    return HttpResponse(final_json,'json')


def ajax_users(request):

    mac_table = NacMactable.objects.all()
    users = []

    for mac in mac_table:
        user_entry = {} 
	status = 1
        if mac.user_id:
	   user_entry['user_id'] = mac.user_id
           if mac.user_id in users:
	      user_entry['num_hosts'] += 1
	   else:
	      user_entry['num_hosts'] = 1 
           user_entry['status'] = switch_button(status)
           users.append(user_entry)

    users_json = json.dumps(users)
    final_json = "{ \"aaData\": \n" + users_json + "\n }"

    return HttpResponse(final_json,'json')




#Functions

def mk_aaData(json_str):

    return "{ \"aaData\": \n" + json_str + "\n }" 

def switch_button(status):
    
    str = ""

    if status == 1:
      str = "<button type=\"button\" class=\"btn btn-danger\">Disable</button>"
    else:
      str = "<button type=\"button\" class=\"btn btn-success\">Activate</button>"

    return str
     

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
        button_style = "btn-danger" 
     elif mac_entry.state == 'PORT':
        state_name  = "Gateway"
        button_style = "btn-success"
     else:
        state_name  = mac_entry.state 
        button_style = "btn-warning"


     button_str = "<div class=\"btn-group\"> <button type=\"button\" data-toggle=\"dropdown\" class=\"btn dropdown-toggle " + button_style + "\">" + state_name + "<span class=\"caret\"></span> </button> <ul class=\"dropdown-menu\" role=\"menu\">"
     for state in states:
        short_state = short_st(state)
        update_str = "'" + state + "','" + mac_entry.mac + "'"
	update_str = "'" + short_state + "','" + mac_entry.mac + "'"
        button_str += "<li><a href=\"\" onclick=\"get_to_url('/cassini/updatedb/'," + update_str + ")\">" + state + "</a></li>"
     button_str += "</ul></div>"
     mac_entry.state = button_str 

  
   return table

def short_st(state):

    if state == "Registration":
      short_state = "REG"
    elif state == "Authenticated":
      short_state = "AUTH"
    elif state == "Operational":
      short_state = "OPER"
    elif state == "Gateway":
      short_state = "PORT"
    elif state == "Quarantine":
      short_state = "QUAR"
    else:
      short_state = "UNK"

    return short_state

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
