.. _auth_ldap:

==============================================
Authentication with an existing LDAP directory
==============================================

Authentic use the module django_auth_ldap to synchronize the Django user tables
with an LDAP. For complex use case, we will refer you to the django_auth_ldap
documentation, see http://packages.python.org/django-auth-ldap/.

How to authenticate users against an LDAP server with anonymous binding ?
-------------------------------------------------------------------------

1. Install the django_auth_ldap module for Django::

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

