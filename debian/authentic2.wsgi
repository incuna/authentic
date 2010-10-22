import os
import sys

# Allows to lookup local_settings.py
sys.path.append('/etc/authentic2')

os.environ['DJANGO_SETTINGS_MODULE'] = 'authentic2.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
