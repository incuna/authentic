#! /usr/bin/env python
#
# Setup script for Authentic
#
# It started as a copy of ReviewBoard setup.py file, thanks to them, and for
import distutils.core
import authentic2
import os

def ls_R(directory):
    '''Recursively list files in @directory'''
    for root, dirs, files in os.walk(directory):
        for file in files:
            yield os.path.join(root, file)

# Build the authentic package.
distutils.core.setup(name="authentic2",
      version=authentic2.VERSION,
      license="GPLv2 or later",
      description="Authentic, a versatile identity server",
      url="http://dev.entrouvert.org/projects/authentic/",
      author="Entr'ouvert",
      author_email="authentic-devel@lists.labs.libre-entreprise.org",
      maintainer="Benjamin Dauvergne",
      maintainer_email="bdauvergne@entrouvert.com",
      py_modules=['manage'],
      packages=[ 'authentic2',
            'authentic2/admin_log_view',
            'authentic2/auth2_auth',
            'authentic2/auth2_auth/auth2_oath',
            'authentic2/auth2_auth/auth2_openid',
            'authentic2/auth2_auth/templatetags',
            'authentic2/authsaml2',
            'authentic2/idp',
            'authentic2/idp/idp_openid',
            'authentic2/idp/idp_openid/templatetags',
            'authentic2/idp/saml',
            'authentic2/idp/templatetags',
            'authentic2/saml',
            'authentic2/saml/management',
            'authentic2/saml/management/commands',
            'authentic2/sslauth',
            'authentic2/vendor',
            'authentic2/vendor/oath',
            'authentic2/vendor/totp_js',],
      package_data={ '': ['fixtures/*.json',
          'templates/*.html','templates/*/*.html','js/*.js'] },
      data_files=[('/share/authentic2/media/', list(ls_R('media')))],
      requires=[
          'django (>=1.2.0)',
          'registration (>=0.7)',
          'debug_toolbar',
          'django_authopenid (>=1.0)',
      ],
)
