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
    url(r'^users/$', views.placeholder),
    url(r'^networks/$', views.placeholder),
    url(r'^about/$', views.about),
    url(r'^contact/$', views.contact),
    url(r'^login/$', views.login),
    url(r'^hosts/$', views.placeholder),
    url(r'^switches/$', views.placeholder),
    url(r'^apps/nac/$', views.placeholder),
    #url(r'^admin/', include('django.contrib.admin.cassini.urls')), 
)
