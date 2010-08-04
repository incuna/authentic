# Django settings for authentic project.

import os

gettext_noop = lambda s: s

DEBUG = True
USE_DEBUG_TOOLBAR = True
STATIC_SERVE = True
TEMPLATE_DEBUG = DEBUG
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_PATH, 'authentic.db'),
    }
}

#session cookie parameters
SESSION_EXPIRE_AT_BROWSER_CLOSE =  True
SESSION_COOKIE_AGE = 36000

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
LANGUAGE_CODE = 'en'

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
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

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
    'django.contrib.messages.context_processors.messages',
    'authentic.core.context_processors.auth_settings',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.csrf.middleware.CsrfMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'authentic.admin_log_view.middleware.LoggerMiddleware',
)

ROOT_URLCONF = 'authentic.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates'),
    os.path.join(PROJECT_PATH, 'templates/django_openid_provider'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.sites',
    'authentic.saml',
    'authentic.idp',
    'authentic.idp.saml',
    'registration',
    'authentic.sslauth',
    'authentic.admin_log_view',
)

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Registration settings
ACCOUNT_ACTIVATION_DAYS = 2
EMAIL_HOST = 'localhost'
DEFAULT_FROM_EMAIL = 'webmaster@entrouvert.com'
LOGIN_REDIRECT_URL = '/'

INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {'INTERCEPT_REDIRECTS': False}

# SAML settings
# Only RSA private keys are currently supported
IDP_SAML2 = True
IDP_IDFF12 = True
SAML_PRIVATE_KEY = '''-----BEGIN RSA PRIVATE KEY-----
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
SAML_METADATA_ROOT = os.path.join(PROJECT_PATH, 'metadata')

# SSL settings
AUTH_SSL = True
SSLAUTH_CREATE_USER = True
AUTHENTICATION_BACKENDS = (
    'authentic.idp.auth_backends.LogginBackend',
    'django.contrib.auth.backends.ModelBackend',
    'authentic.sslauth.backends.SSLAuthBackend',
)

#AuthSAML2 Configuration
INSTALLED_APPS += ('authentic.authsaml2',)
SAML2_BACKEND = 'authentic.authsaml2.backends.AuthSAML2Backend'
AUTHENTICATION_BACKENDS += (SAML2_BACKEND,)
TEMPLATE_CONTEXT_PROCESSORS += ('authentic.idp.views.authsaml2_login_page',)

# OpenID settings
AUTH_OPENID = True
IDP_OPENID = True
IDPOI_PATH = ''

# Logging settings
LOG_FILENAME = 'log.log'
LOG_FILE_LEVEL = 10 #CRITICAL 50 ERROR 40 WARNING 30 INFO 20 DEBUG 10
LOG_SYSLOG = True
LOG_SYS_LEVEL = 10

# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
try:
    from local_settings import *
except ImportError:
    pass

if USE_DEBUG_TOOLBAR:
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
    INSTALLED_APPS += ('debug_toolbar',)

if AUTH_OPENID:
    MIDDLEWARE_CLASSES += ('django_authopenid.middleware.OpenIDMiddleware',)
    INSTALLED_APPS += ('django_authopenid',)

if IDP_OPENID:
    INSTALLED_APPS += ('django_openid_provider',
                    'openid_provider',)
