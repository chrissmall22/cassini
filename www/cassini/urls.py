from django.conf.urls import patterns, include, url
from cassini import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    #url(r'^mysite/', include('admin.site.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.overview), 
    url(r'^users/$', views.users),
    url(r'^networks/$', views.networks),
    url(r'^about/$', views.about),
    url(r'^contact/$', views.contact),
    url(r'^login/$', views.login),
    url(r'^hosts/$', views.hosts),
    url(r'^switches/$', views.switches),
    url(r'^projects/$', views.projects),

    # Applications
    url(r'^apps/$', views.apps),
    url(r'^apps/nac/$', views.hosts),
    #url(r'^admin/', include('django.contrib.admin.cassini.urls')), 

    # AJAX Web Services URLS
    url(r'^ajax/hosts$' , views.ajax_hosts),
    url(r'^ajax/users$' , views.ajax_users),
    url(r'^ajax/switches$' , views.ajax_switches),
    url(r'^ajax/projects$' , views.ajax_projects), 

    # Database POST updates
    url(r'^updatedb/$' , views.update_db),
)

