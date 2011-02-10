import os 
os.environ['DJANGO_SETTINGS_MODULE'] = 'authentic2.settings'
try:
    import django
    print 'Django:', django.get_version()
except ImportError:
    print 'django is missing: easy_install django'
    sys.exit(1)

try:
    import south
    print 'South:', south.__version__
except ImportError:
    print 'south is missing: easy_isntall south'
try:
    import django_authopenid
    print 'Django-authopenid:', django_authopenid.__version__
except ImportError:
    raise
    print 'django_authopenid is missing: easy_install django-authopenid'

try:
    import registration
except ImportError:
    print 'registration is missing: easy_install django-registration'
