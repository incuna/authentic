# Django settings for authentic project.

import os

gettext_noop = lambda s: s

DEBUG = True
USE_DEBUG_TOOLBAR = DEBUG
STATIC_SERVE = DEBUG
TEMPLATE_DEBUG = DEBUG
_PROJECT_PATH = os.path.join(os.path.dirname(__file__), '..')

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(_PROJECT_PATH, 'authentic2/authentic.db')
    }
}

#session cookie parameters
SESSION_EXPIRE_AT_BROWSER_CLOSE =  True
SESSION_COOKIE_AGE = 36000 # one day of work

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fr'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

LANGUAGES = (
    ('en', gettext_noop('English')),
    ('fr', gettext_noop('French')),
)

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(_PROJECT_PATH, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"

STATIC_ROOT = os.path.join(_PROJECT_PATH, 'static')
STATIC_URL = '/static/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '0!=(1kc6kri-ui+tmj@mr+*0bvj!(p*r0duu2n=)7@!p=pvf9n'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.static',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'django.contrib.csrf.middleware.CsrfMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'authentic2.idp.middleware.DebugMiddleware'
)

ROOT_URLCONF = 'authentic2.urls'

TEMPLATE_DIRS = (
    # authentic2/templates
    os.path.join(os.path.dirname(__file__), 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.staticfiles',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.sites',
    'authentic2.nonce',
    'authentic2.saml',
    'authentic2.idp',
    'authentic2.idp.saml',
    'registration',
    'authentic2.auth2_auth',
    'authentic2.auth2_auth.auth2_openid',
    'authentic2.auth2_auth.auth2_oath',
    'authentic2.auth2_auth.auth2_ssl',
    'south',
    'authentic2.attribute_aggregator',
)

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

LOGIN_URL = '/login'

# Registration settings
ACCOUNT_ACTIVATION_DAYS = 2
EMAIL_HOST = 'localhost'
DEFAULT_FROM_EMAIL = 'webmaster@localhost'
LOGIN_REDIRECT_URL = '/'
# Default profile class
AUTH_PROFILE_MODULE = 'idp.UserProfile'

INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {'INTERCEPT_REDIRECTS': False}

###########################
# Authentication settings
###########################

# Only RSA private keys are currently supported
AUTH_FRONTENDS = ( 'authentic2.auth2_auth.backend.LoginPasswordBackend',)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

# expiration in seconds of authentication events.
# default: 1 week
# AUTHENTICATION_EVENT_EXPIRATION = 3600*24*7

# SSL Authentication
AUTH_SSL = True
SSLAUTH_CREATE_USER = True

# SAML2 Authentication
AUTH_SAML2 = True

# OpenID Authentication
AUTH_OPENID = True

# OATH Authentication
AUTH_OATH = True

#############################
# Identity Provider settings
#############################

# List of IdP backends, mainly used to show available services in the homepage
# of user, and to handle SLO for each protocols
IDP_BACKENDS = [ ]

# SAML2 IDP
IDP_SAML2 = True

# You MUST changes these keys, they are just for testing !
LOCAL_METADATA_CACHE_TIMEOUT = 600
SAML_SIGNATURE_PUBLIC_KEY = '''-----BEGIN CERTIFICATE-----
MIIDIzCCAgugAwIBAgIJANUBoick1pDpMA0GCSqGSIb3DQEBBQUAMBUxEzARBgNV
BAoTCkVudHJvdXZlcnQwHhcNMTAxMjE0MTUzMzAyWhcNMTEwMTEzMTUzMzAyWjAV
MRMwEQYDVQQKEwpFbnRyb3V2ZXJ0MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIB
CgKCAQEAvxFkfPdndlGgQPDZgFGXbrNAc/79PULZBuNdWFHDD9P5hNhZn9Kqm4Cp
06Pe/A6u+g5wLnYvbZQcFCgfQAEzziJtb3J55OOlB7iMEI/T2AX2WzrUH8QT8NGh
ABONKU2Gg4XiyeXNhH5R7zdHlUwcWq3ZwNbtbY0TVc+n665EbrfV/59xihSqsoFr
kmBLH0CoepUXtAzA7WDYn8AzusIuMx3n8844pJwgxhTB7Gjuboptlz9Hri8JRdXi
VT9OS9Wt69ubcNoM6zuKASmtm48UuGnhj8v6XwvbjKZrL9kA+xf8ziazZfvvw/VG
Tm+IVFYB7d1x457jY5zjjXJvNysoowIDAQABo3YwdDAdBgNVHQ4EFgQUeF8ePnu0
fcAK50iBQDgAhHkOu8kwRQYDVR0jBD4wPIAUeF8ePnu0fcAK50iBQDgAhHkOu8mh
GaQXMBUxEzARBgNVBAoTCkVudHJvdXZlcnSCCQDVAaInJNaQ6TAMBgNVHRMEBTAD
AQH/MA0GCSqGSIb3DQEBBQUAA4IBAQAy8l3GhUtpPHx0FxzbRHVaaUSgMwYKGPhE
IdGhqekKUJIx8et4xpEMFBl5XQjBNq/mp5vO3SPb2h2PVSks7xWnG3cvEkqJSOeo
fEEhkqnM45b2MH1S5uxp4i8UilPG6kmQiXU2rEUBdRk9xnRWos7epVivTSIv1Ncp
lG6l41SXp6YgIb2ToT+rOKdIGIQuGDlzeR88fDxWEU0vEujZv/v1PE1YOV0xKjTT
JumlBc6IViKhJeo1wiBBrVRIIkKKevHKQzteK8pWm9CYWculxT26TZ4VWzGbo06j
o2zbumirrLLqnt1gmBDvDvlOwC/zAAyL4chbz66eQHTiIYZZvYgy
-----END CERTIFICATE-----'''

SAML_SIGNATURE_PRIVATE_KEY = '''-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAvxFkfPdndlGgQPDZgFGXbrNAc/79PULZBuNdWFHDD9P5hNhZ
n9Kqm4Cp06Pe/A6u+g5wLnYvbZQcFCgfQAEzziJtb3J55OOlB7iMEI/T2AX2WzrU
H8QT8NGhABONKU2Gg4XiyeXNhH5R7zdHlUwcWq3ZwNbtbY0TVc+n665EbrfV/59x
ihSqsoFrkmBLH0CoepUXtAzA7WDYn8AzusIuMx3n8844pJwgxhTB7Gjuboptlz9H
ri8JRdXiVT9OS9Wt69ubcNoM6zuKASmtm48UuGnhj8v6XwvbjKZrL9kA+xf8ziaz
Zfvvw/VGTm+IVFYB7d1x457jY5zjjXJvNysoowIDAQABAoIBAQCj8t2iKXya10HG
V6Saaeih8aftoLBV38VwFqqjPU0+iKqDpk2JSXBhjI6s7uFIsaTNJpR2Ga1qvns1
hJQEDMQSLhJvXfBgSkHylRWCpJentr4E3D7mnw5pRsd61Ev9U+uHcdv/WHP4K5hM
xsdiwXNXD/RYd1Q1+6bKrCuvnNJVmWe0/RV+r3T8Ni5xdMVFbRWt/VEoE620XX6c
a9TQPiA5i/LRVyie+js7Yv+hVjGOlArtuLs6ECQsivfPrqKLOBRWcofKdcf+4N2e
3cieUqwzC15C31vcMliD9Hax9c1iuTt9Q3Xzo20fOSazAnQ5YBEExyTtrFBwbfQu
ku6hp81pAoGBAN6bc6iJtk5ipYpsaY4ZlbqdjjG9KEXB6G1MExPU7SHXOhOF0cDH
/pgMsv9hF2my863MowsOj3OryVhdQhwA6RrV263LRh+JU8NyHV71BwAIfI0BuVfj
6r24KudwtUcvMr9pJIrJyMAMaw5ZyNoX7YqFpS6fcisSJYdSBSoxzrzVAoGBANu6
xVeMqGavA/EHSOQP3ipDZ3mnWbkDUDxpNhgJG8Q6lZiwKwLoSceJ8z0PNY3VetGA
RbqtqBGfR2mcxHyzeqVBpLnXZC4vs/Vy7lrzTiHDRZk2SG5EkHMSKFA53jN6S/nJ
JWpYZC8lG8w4OHaUfDHFWbptxdGYCgY4//sjeiuXAoGBANuhurJ99R5PnA8AOgEW
4zD1hLc0b4ir8fvshCIcAj9SUB20+afgayRv2ye3Dted1WkUL4WYPxccVhLWKITi
rRtqB03o8m3pG3kJnUr0LIzu0px5J/o8iH3ZOJOTE3iBa+uI/KHmxygc2H+XPGFa
HGeAxuJCNO2kAN0Losbnz5dlAoGAVsCn94gGWPxSjxA0PC7zpTYVnZdwOjbPr/pO
LDE0cEY9GBq98JjrwEd77KibmVMm+Z4uaaT0jXiYhl8pyJ5IFwUS13juCbo1z/u/
ldMoDvZ8/R/MexTA/1204u/mBecMJiO/jPw3GdIJ5phv2omHe1MSuSNsDfN8Sbap
gmsgaiMCgYB/nrTk89Fp7050VKCNnIt1mHAcO9cBwDV8qrJ5O3rIVmrg1T6vn0aY
wRiVcNacaP+BivkrMjr4BlsUM6yH4MOBsNhLURiiCL+tLJV7U0DWlCse/doWij4U
TKX6tp6oI+7MIJE6ySZ0cBqOiydAkBePZhu57j6ToBkTa0dbHjn1WA==
-----END RSA PRIVATE KEY-----'''

SAML_METADATA_ROOT = 'metadata'
# Whether to autoload SAML 2.0 identity providers and services metadata
# Only https URLS are accepted.
# Can be none, sp, idp or both
SAML_METADATA_AUTOLOAD = 'none'

# OpenID settings
IDP_OPENID = True

# CAS settings
IDP_CAS = False
# expiration time in seconds of the cas tickets
# CAS_TICKET_EXPIRATION = 240

# Logging settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)-8s %(name)s.%(message)s',
            'datefmt': '%Y-%m-%d %a %H:%M:%S'
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'console': {
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'local_file': {
            'level':'DEBUG',
            'class':'logging.FileHandler',
            'formatter': 'verbose',
            'filename': os.path.join(_PROJECT_PATH, 'log.log'),
        },
        'syslog': {
            'level':'INFO',
            'class':'logging.handlers.SysLogHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        }
    },
    'loggers': {
        'django': {
            'handlers':['null'],
            'propagate': True,
            'level':'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
    'root': {
            'handlers': ['console', 'local_file'],
            'level': 'DEBUG',
    }
}

# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
try:
    from local_settings import *
except ImportError, e:
    if 'local_settings' in e.args[0]:
        pass

if USE_DEBUG_TOOLBAR:
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
    INSTALLED_APPS += ('debug_toolbar',)

if AUTH_SAML2:
    INSTALLED_APPS += ('authentic2.authsaml2',)
    AUTHENTICATION_BACKENDS += (
            'authentic2.authsaml2.backends.AuthSAML2PersistentBackend',
            'authentic2.authsaml2.backends.AuthSAML2TransientBackend')
    AUTH_FRONTENDS += ('authentic2.authsaml2.frontend.AuthSAML2Frontend',)
    IDP_BACKENDS += ('authentic2.authsaml2.backends.AuthSAML2Backend',)
    DISPLAY_MESSAGE_ERROR_PAGE = True

if AUTH_OPENID:
    INSTALLED_APPS += ('django_authopenid',)
    AUTH_FRONTENDS += ('authentic2.auth2_auth.auth2_openid.backend.OpenIDFrontend',)

if AUTH_SSL:
    AUTHENTICATION_BACKENDS += ('authentic2.auth2_auth.auth2_ssl.backend.SSLBackend',)
    AUTH_FRONTENDS += ('authentic2.auth2_auth.auth2_ssl.frontend.SSLFrontend',)

if AUTH_OATH:
    AUTHENTICATION_BACKENDS += ('authentic2.auth2_auth.auth2_oath.backend.OATHTOTPBackend',)
    AUTH_FRONTENDS += ('authentic2.auth2_auth.auth2_oath.frontend.OATHOTPFrontend',)

if IDP_SAML2:
    IDP_BACKENDS += ('authentic2.idp.saml.backend.SamlBackend',)

if IDP_OPENID:
    INSTALLED_APPS += ('authentic2.idp.idp_openid',)
    TEMPLATE_CONTEXT_PROCESSORS += ('authentic2.idp.idp_openid.context_processors.openid_meta',)

if IDP_CAS:
    INSTALLED_APPS += ('authentic2.idp.idp_cas',)
