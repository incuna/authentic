#! /usr/bin/env python
#
# Setup script for Authentic
#
# It started as a copy of ReviewBoard setup.py file, thanks to them, and for
import distutils.core
import authentic2

# Build the authentic package.
distutils.core.setup(name="authentic2",
      version=authentic2.VERSION,
      license="GPLv2 or later",
      description="Authentic, a versatile identity server",
      url="http://authentic.labs.libre-entreprise.org/",
      author="Entr'ouvert",
      author_email="authentic-devel@lists.labs.libre-entreprise.org",
      maintainer="Benjamin Dauvergne",
      maintainer_email="bdauvergne@entrouvert.com",
      py_modules=['manage'],
      packages=[ 'authentic2',
            'authentic2/django_openid_provider',
            'authentic2/core',
            'authentic2/sslauth',
            'authentic2/saml',
            'authentic2/authsaml2',
            'authentic2/admin_log_view',
            'authentic2/idp',
            'authentic2/idp/templatetags',
            'authentic2/idp/saml'],
      package_data={ '': ['fixtures/*.json',
          'templates/*.html','templates/*/*.html'] },
      requires=[
          'django (>=1.2.0)',
          'registration (>=0.7)',
          'debug_toolbar',
          'django_authopenid (>=1.0)',
      ],
)
