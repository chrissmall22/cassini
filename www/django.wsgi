import os, sys
sys.path.append('/home/chsmall/pox/ext/cassini/www')
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
