from django.conf.urls import patterns, include, url
from mysite.views import overview, switches, placeholder, about, contact, login, register

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
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', overview),
    url(r'^switch/$', switches),
    url(r'^user/$', placeholder),
    url(r'^network/$', placeholder),
    url(r'^workgroup/$', placeholder),
    url(r'^about/$', about),
    url(r'^contact/$', contact),
    url(r'^login/$', login),
    url(r'^register/$', register),
)
