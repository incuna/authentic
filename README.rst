=====================================
Authentic - Versatile Identity Server
=====================================

Authentic is a versatile identity provider aiming to address a broad
range of needs, from simple to complex setups; it has support for many
protocols and can bridge between them.

It has support for SAMLv2 thanks to Lasso, a free (GNU GPL)
implementation of the Liberty Alliance specifications.

Dependencies
------------

You must install the following packages to use Authentic

 * Python Lasso binding::

   From sources: http://lasso.entrouvert.org/download
   Debian based distribution: apt-get install python-lasso


 * Django-registration::

    From sources: http://bitbucket.org/ubernostrum/django-registration/downloads
    Debian based distribution: apt-get install python-django-registration

 * Django-debug-toolbar (optional)::

    From sources: http://github.com/robhudson/django-debug-toolbar/downloads
    Debian based distribution: apt-get install python-django-registration

 * Django-authopenid::

   From sources: http://bitbucket.org/benoitc/django-authopenid/downloads

 * Django-south::

   From sources:: http://south.aeracode.org/docs/installation.html

You install all the django libraries quickly using pip::

   pip install django django-registration django-debug-toolbar django-authopenid south

or easy_install::

   easy_install django django-registration django-debug-toolbar django-authopenid south

Quick Start
-----------

Then launch the following commands::

  python manage.py syncdb --migrate
  python manage.py runserver

You should see the following output::

  Validating models...
  0 errors found

  Django version 1.2, using settings 'authentic.settings'
  Development server is running at http://127.0.0.1:8000/
  Quit the server with CONTROL-C.

  You can access the running application on http://127.0.0.1:8000/


Specifying a different database
-------------------------------

This is done by modifying the DATABASES dictionary in your local_settings.py file
(create it in Authentic project directory); for example::

 DATABASES['default'] = {
   'ENGINE': 'django.db.backends.postgresql',
   'NAME': 'authentic',
   'USER': 'admindb',
   'PASSWORD': 'foobar',
   'HOST': 'db.example.com',
   'PORT': '', # empty string means default value
 }

You should refer to the Django documentation on databases settings at
http://docs.djangoproject.com/en/dev/ref/settings/#databases for all
the details.

How to authenticate users against an LDAP server with anonymous binding ?
-------------------------------------------------------------------------

1. Install the django_auth_ldap module for Django::

  pip install django_auth_ldap

2. Configure your local_settings.py file for authenticating agains LDAP.
   The next lines must be added::

 import ldap
 from django_auth_ldap.config import LDAPSearch

 # Here put the LDAP URL of your server
 AUTH_LDAP_SERVER_URI = 'ldap://ldap.example.com'
 # Let the bind DN and bind password blank for anonymous binding
 AUTH_LDAP_BIND_DN = ""
 AUTH_LDAP_BIND_PASSWORD = ""
 # Lookup user under the branch o=base and by mathcing their uid against the
 # received login name
 AUTH_LDAP_USER_SEARCH = LDAPSearch("o=base",
     ldap.SCOPE_SUBTREE, "(uid=%(user)s)") 

How to I authenticate against Authentic2 with a SAMLv2 service provider ?
------------------------------------------------------------------------

1. Get the metadata file from the URL::

 htpp[s]://idp-hostname/idp/saml2/metadata

And configure your service provider with it.

2. Go to the providers admin panel on::

 http[s]://admin/saml/libertyprovider/add/

There create a new provider using the service provider metadata and enable it
as a service provider, you can customize some behaviours like the preferred
assertion consumer or encryption for the NameID or the Assertion element.

How to upgrade to a new version of authentic ?
----------------------------------------------

Authentic store all its data in a relational database as specified in its
settings.py or local_settings.py file. So in order to upgrade to a new version
of authentic you have to update your database schema using the
migration command — you will need to have installed the dependency django-south,
see the beginning of this README file.::

  python ./manage.py migrate

Then you will need to create new tables if there are.::

  python ./manage.py syncdb

Copyright
---------

Authentic is copyrighted by Entr'ouvert and is licensed through the GNU General
Public Licence, version 2 or later. A copy of the whole license text is
available in the COPYING file.

