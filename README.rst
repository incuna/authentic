=====================================
Authentic - Versatile Identity Server
=====================================

Authentic is a versatile identity provider aiming to address a broad
range of needs, from simple to complex setups; it has support for many
protocols and can bridge between them.

It has support for ID-FF and SAMLv2 thanks to Lasso, a free (GNU GPL)
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

 * Django-debug-toolbar::

    From sources: http://github.com/robhudson/django-debug-toolbar/downloads
    Debian based distribution: apt-get install python-django-registration

 * Django-authopenid::

   From sources: http://bitbucket.org/benoitc/django-authopenid/downloads


Quick Start
-----------

Then launch the following commands::

  python manage.py syncdb
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

Copyright
---------

Authentic is copyrighted by Entr'ouvert and is licensed through the GNU General
Public Licence, version 2 or later. A copy of the whole license text is
available in the COPYING file.

