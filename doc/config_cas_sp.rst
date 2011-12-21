.. _config_cas_sp:

=====================================
Configure Authentic 2 as a CAS server
=====================================

How to use Authentic 2 as a CAS 1.0 or CAS 2.0 identity provider ?
------------------------------------------------------------------

1. Activate CAS IdP support in settings.py::

     IDP_CAS = True

2. Then create the database table to hold CAS service tickets::

    python authentic2/manage.py syncdb --migrate

3. Also configure authentic2 to authenticate against your LDAP directory (see
   above) if your want your user attributes to be accessible from your service,
   if it is not necessary you can use the normal relational database storage
   for you users.

4. Finally configure your service to point to the CAS endpoint at:

    http[s]://your.domain.com/idp/cas/

5. If needed configure your service to resolve authenticated user with your
   LDAP directory (if user attributes are needed for your service)
