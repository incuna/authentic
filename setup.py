#! /usr/bin/env python
#
# Setup script for Authentic
#
# It started as a copy of ReviewBoard setup.py file, thanks to them, and for
import distutils.core
import authentic2
import os

def ls_R(directory, target):
    '''Recursively list files in @directory'''
    path = os.path.join(os.path.dirname(__file__), directory)
    to_remove = os.path.dirname(path)
    for root, dirs, files in os.walk(path):
        root = root.replace(to_remove + '/', '')
        file_list = [ os.path.join(root, file) for file in files]
        yield (os.path.join(target, root), file_list)

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
      packages=[ 'authentic2',
            'authentic2/admin_log_view',
            'authentic2/auth2_auth',
            'authentic2/auth2_auth/auth2_oath',
            'authentic2/auth2_auth/auth2_ssl',
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
            'authentic2/vendor',
            'authentic2/vendor/oath',
            'authentic2/vendor/totp_js',
            'authentic2/saml/migrations',
            'authentic2/auth2_auth/auth2_oath/migrations',
            'authentic2/auth2_auth/auth2_ssl/migrations',
            'authentic2/auth2_auth/migrations',
            'authentic2/authsaml2/migrations',
            'authentic2/idp/idp_openid/migrations',
            ],
      package_data={ '': ['fixtures/*.json',
          'templates/*.html','templates/*/*.html','js/*.js'] },
      data_files=list(ls_R('media', 'share/authentic2/')),
      requires=[
          'django (>=1.2.0)',
          'registration (>=0.7)',
          'debug_toolbar',
          'django_authopenid (>=1.0)',
      ],
)
