.. Authentic2 documentation master file, created by
   sphinx-quickstart on Thu Oct 13 09:53:03 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==========================
Authentic2's documentation
==========================

Authentic2 is a versatile identity provider addressing a broad
range of needs, from simple to advanced setups, around web authentication,
attribute sharing and namespace mapping.

Authentic2 supports many protocols and standards, including SAML2, CAS, OpenID,
LDAP, X509, OATH, and can bridge between them.

Authentic2 is under the GNU AGPL version 3 licence.

It has support for SAMLv2 thanks to `Lasso <http://lasso.entrouvert.org>`_,
a free (GNU GPL) implementation of the Liberty Alliance and OASIS
specifications of SAML2, ID-FF1.2 and ID-WSF2.

The Documentation is under the licence Creative Commons `CC BY-SA 2.0 <http://creativecommons.org/licenses/by-sa/2.0/>`_.

- `Authentic2 project site <http://dev.entrouvert.org/projects/authentic>`_
- `Authentic2 roadmap <http://dev.entrouvert.org/projects/authentic/roadmap>`_
- `Documentation in PDF <https://dev.entrouvert.org/attachments/158/Authentic2.pdf>`_

Documentation content
=====================

.. toctree::
   :maxdepth: 2

   features

   download

   installation

   settings

   auth_ldap

   auth_pam

   administration_with_policies

   where_metadata

   config_saml2_sp

   config_saml2_idp

   saml2_slo

   sync-metadata_script

   config_cas_sp

   attribute_management

   attribute_management_explained

   attributes_in_session

   consent_management

Copyright
=========

Authentic and Authentic2 are copyrighted by Entr'ouvert and are licensed
through the GNU AFFERO GENERAL PUBLIC LICENSE, version 3 or later. A copy of
the whole license text is available in the COPYING file.

The OpenID IdP originates in the project django_openid_provider by Roman
Barczyski, which is under the Apache 2.0 licence. This imply that you must
distribute authentic2 under the AGPL3 licence when distributing this part of the
project which is the only AGPL licence version compatible with the Apache 2.0
licence.

The Documentation is under the licence Creative Commons
`CC BY-SA 2.0 <http://creativecommons.org/licenses/by-sa/2.0/>`_.

.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`
