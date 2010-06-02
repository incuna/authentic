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
)

ROOT_URLCONF = 'authentic.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'authentic.idp',
    'authentic.idp.saml',
    'registration',
    'authentic.idp.saml',
    'authentic.sslauth',
)

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
MIICXgIBAAKBgQCtTbDTe/LrD+gvK0Sgf/rnvAg4zcc/vJcEdsiGsJ3shTse7OPf
5fIaD7lry+jmtFX61n8Rn1d1iw+whuYbrG6R3OhDw50vufb2RrRSHBOA7CcfiKQD
6CT2p31msv+CiHbGmoHRFyt2CnRGy2FCX2Oizf5qxfjHaJEXu0tk/SdN2QIDAQAB
AoGBAKlFVQ17540JAHPyAxnxZxSpaC5zb8YlYiwOCVblc5rtlw1hvEGYy5wA987+
YAHW6pQSphKEXFyG81Asst0c0vExgGVFjzAy/GFrBTnl0l5PtwPDDIAmGP6DQw4C
lOHJePloKp0xjCo2nJ8XluxkPp1+XtJyJOhZWpQPDvF3uL+xAkEA3t58jg0SV55s
E10R04QOJB0qIB9U4Nw29uhh5RXv8JRq41pw4iDmpi9I67nGqDeuxlDUQ/+5rLOE
Ptp07BsFWwJBAMcQ7wiwhIYtRC8ff3WbWX9wcABDyX47uYvAMIiaEOmFmJyI41mW
xlik821Aaid1Z45vgBN32hYkEbpWaaIVe9sCQQCX7mpQ2F5ptskMhkTxwbN2MR+X
mGRfiiA6P/8EkejpQ/R+GxibPzydi9yVPidMY/FUpqOd24YzUonT408T6fPDAkEA
pkkt86tIOLEtaNO97CcF/t+Un5QAh9MqLmQv5pwUDo4Lqo7qo1bAfyHjOlr5kdaP
17qqWRjf82jT6jzu5nddywJAVQpxlZ8fIZUzTD2mRQeLf5O+rXmtH1LlwRRGCNaa
8eM47A92x9uplD/sN550pTKM7XLhHBvEfLujUoGHpWQxGA==
-----END RSA PRIVATE KEY-----'''

# SSL settings
AUTH_SSL = True
SSLAUTH_CREATE_USER = True
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'authentic.sslauth.backends.SSLAuthBackend',
)

# OpenID settings
AUTH_OPENID = True
IDP_OPENID = True

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

