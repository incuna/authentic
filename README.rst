=======================================
Authentic 2 - Versatile Identity Server
=======================================

Authentic 2 is a versatile identity provider aiming to address a broad
range of needs, from simple to complex setups; it has support for many
protocols and can bridge between them.

Authentic 2 is under the GNU AGPL version 3 licence.

It has support for SAMLv2 thanks to Lasso, a free (GNU GPL)
implementation of the Liberty Alliance specifications.

Features
--------

Authentic can authenticate users against:
 - an LDAP directory,
 - a SAML 2.0 identity provider,
 - an OpenID identity provider,
 - with an X509 certificate.

Authentic can provide authentication to web applications using the following
protocols:
 - OpenID,
 - SAML 2.0,
 - CAS 1.0 & CAS 2.0.

Authentic can proxy authentication between any two different protocols it
support.

Installation
============

Dependencies
------------

You must install the following packages to use Authentic

 * Python Lasso binding 2.3.6::

   From sources: http://lasso.entrouvert.org/download
   Debian based distribution: apt-get install python-lasso

 * Django 1.3::

   From sources: http://www.djangoproject.com/download/1.3/tarball/

 * Django-registration 0.8-alpha-1::

    From sources: http://bitbucket.org/ubernostrum/django-registration/downloads
    Debian based distribution: apt-get install python-django-registration

 * Django-authopenid 0.9.6::

   From sources: http://bitbucket.org/benoitc/django-authopenid/downloads

 * Django-south 0.7.3::

   From sources:: http://south.aeracode.org/docs/installation.html

 * Django-profiles 0.2::

   From sources:: http://pypi.python.org/pypi/django-profiles

You install all the django libraries quickly using pip::

   pip install django django-profiles django-registration \
               django-debug-toolbar django-authopenid south

or easy_install::

   easy_install django django-profiles django-registration \
                django-debug-toolbar django-authopenid south

Quick Start
-----------

Then launch the following commands::

  python manage.py syncdb --migrate
  python manage.py collectstatic
  python manage.py runserver

You should see the following output::

  Validating models...
  0 errors found

  Django version 1.3, using settings 'authentic.settings'
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

Using Authentic with an LDAP directory
======================================

Authentic use the module django_auth_ldap to synchronize the Django user tables
with an LDAP. For complex use case, we will refer you to the django_auth_ldap
documentation, see http://packages.python.org/django-auth-ldap/.

How to authenticate users against an LDAP server with anonymous binding ?
-------------------------------------------------------------------------

1. Install the django_auth_ldap module for Django, for this you need
   python-ldap, python-ldap needs python developement headers to be installed
   but is usually packaged by most distributions::

 pip install django_auth_ldap


2. Configure your local_settings.py file for authenticating against LDAP.
   The next lines must be added::

 AUTHENTICATION_BACKENDS += ( 'django_auth_ldap.backend.LDAPBackend', )

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

How to allow members of an LDAP group to manage Authentic ?
-----------------------------------------------------------

1. First you must know the objectClass of groups in your LDAP schema, this FAQ
   will show you the configuration for two usual classes: groupOfNames and
   groupOfUniqueNames.

2. Find the relevant groupname. We will say it is: cn=admin,o=mycompany

3. Add the following lines::

  from django_auth_ldap.config import GroupOfNamesType
  AUTH_LDAP_GROUP_TYPE = GroupOfNamesType()
  AUTH_LDAP_GROUP_SEARCH = LDAPSearch("o=mycompany",
            ldap.SCOPE_SUBTREE, "(objectClass=groupOfNames)")
  AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_staff": "cn=admin,o=mycompany"
  }

For an objectClass of groupOfUniqueNames you would change the string
GroupOfNamesType to GroupOfUniqueNamesType and grouOfNames to
groupOfUniqueNames. For more complex cases see the django_auth_ldap
documentation.

SAML 2.0
========

How to I authenticate against Authentic 2 with a SAMLv2 service provider ?
------------------------------------------------------------------------

 http[s]://your.domain.com/idp/saml2/metadata

And configure your service provider with it.

2. Go to the providers admin panel on::

 http[s]://admin/saml/libertyprovider/add/

There create a new provider using the service provider metadata and enable it
as a service provider, you can customize some behaviours like the preferred
assertion consumer or encryption for the NameID or the Assertion element.

CAS
===

How to use Authentic 2 as a CAS 1.0 or CAS 2.0 identity provider ?
-----------------------------------------------------------------

1. Activate CAS IdP support in settings.py::

 IDP_CAS = True

2. Then create the database table to hold CAS service tickets::

 python authentic2/manage.py syncdb --migrate

2. Also configure authentic2 to authenticate against your LDAP directory (see
   above) if your want your user attributes to be accessible from your service,
   if it is not necessary you can use the normal relational database storage
   for you users.

3. Finally configure your service to point to the CAS endpoint at::

 http[s]://your.domain.com/idp/cas/

4. If needed configure your service to resolve authenticated user with your
   LDAP directory (if user attributes are needed for your service)


PAM authentication
==================

This module is copied from https://bitbucket.org/wnielson/django-pam/ by Weston
Nielson and the pam ctype module by Chris Atlee http://atlee.ca/software/pam/.

Add 'authentic2.vendor.dpam.backends.PAMBackend' to your
``settings.py``::

  AUTHENTICATION_BACKENDS = (
      ...
      'authentic2.vendor.dpam.backends.PAMBackend',
      ...
  )

Now you can login via the system-login credentials.  If the user is
successfully authenticated but has never logged-in before, a new ``User``
object is created.  By default this new ``User`` has both ``is_staff`` and
``is_superuser`` set to ``False``.  You can change this behavior by adding
``PAM_IS_STAFF=True`` and ``PAM_IS_SUPERUSER`` in your ``settings.py`` file.

The default PAM service used is ``login`` but you can change it by setting the
``PAM_SERVICE`` variable in your ``settings.py`` file.

Roadmap
=======

 - All (or nearly) settings will be configurable from the /admin panels
 - Login page will remember user choices for authentication and authenticate
   the user passively using hidden iframes
 - After a logout no passive login will be done
 - CAS IdP will allow to whitelist service URL and proxy granting ticket URLs,
   and to refuse request from unkown URLs. It will also allow to use patterns
   as URLs.
 - Extended CAS 2.0, with SAML attribute inside the CAS 2.0 validated ticket.
 - A virtual LDAP directory based on the OpenLDAP socket backend would remove
   the need for a real LDAP directory to pass user attributes to CAS relying
   parties.
 - WS-Trust token service endpoint
 - Email forwarder, so that relying parties never get the real user email.
 - Support slo in the CAS logout endpoint

Copyright
---------

Authentic is copyrighted by Entr'ouvert and is licensed through the GNU General
Public Licence, version 2 or later. A copy of the whole license text is
available in the COPYING file.

The OpenID IdP originates in the project django_openid_provider by Roman
Barczy¿ski, which is under the Apache 2.0 licence. This imply that you must
distribute authentic2 under the AGPL3 licence when distributing this part of the
project which is the only AGPL licence version compatible with the Apache 2.0
licence.
