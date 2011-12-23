.. _installation:

============
Installation
============

Dependencies
------------

You must install the following packages to use Authentic

- Python Lasso binding 2.3.6:

   From sources: http://lasso.entrouvert.org/download
   Debian based distribution: apt-get install python-lasso

- Django 1.3:

   From sources: http://www.djangoproject.com/download/1.3/tarball/

- Django-registration 0.8-alpha-1:

    From sources: http://bitbucket.org/ubernostrum/django-registration/downloads
    Debian based distribution: apt-get install python-django-registration

- Django-authopenid 0.9.6:

   From sources: http://bitbucket.org/benoitc/django-authopenid/downloads

- Django-south 0.7.3:

   From sources:: http://south.aeracode.org/docs/installation.html

- Django-profiles 0.2:

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
