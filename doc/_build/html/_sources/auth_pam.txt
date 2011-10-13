.. _auth_pam:

=====================================
Authentication on Authentic2 with PAM
=====================================

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
