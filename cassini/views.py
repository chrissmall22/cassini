from django.template.loader import get_template
from django.template import Template, Context
from django.http import HttpResponse

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render

import datetime

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
    html = t.render(Context({'current_date': now}))
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


# Functions

def get_stats():
    now = datetime.datetime.now()
    stats = {'current_date': now,
                 'tot_hosts' : 25,
                 'tot_switches': 2,
                 'tot_users': 20}
    return stats
