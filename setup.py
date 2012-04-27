#! /usr/bin/env python
#
'''
   Setup script for Authentic 2
'''
import distutils.core
import authentic2
import os

def ls_r(directory, target):
    '''Recursively list files in @directory'''
    path = os.path.join(os.path.dirname(__file__), directory)
    to_remove = os.path.dirname(path)
    for root, _, files in os.walk(path):
        root = root.replace(to_remove + '/', '')
        file_list = [ os.path.join(root, filename) for filename in files]
        yield (os.path.join(target, root), file_list)

# Build the authentic package.
distutils.core.setup(name="authentic2",
      version=authentic2.VERSION,
      license="AGPLv3 or later",
      description="Authentic 2, a versatile identity management server",
      url="http://dev.entrouvert.org/projects/authentic/",
      author="Entr'ouvert",
      author_email="authentic-devel@lists.labs.libre-entreprise.org",
      maintainer="Benjamin Dauvergne",
      maintainer_email="bdauvergne@entrouvert.com",
      packages=[ 'authentic2',
            'authentic2/admin_log_view',
            'authentic2/attribute_aggregator',
            'authentic2/attribute_aggregator/migrations',
            'authentic2/auth2_auth',
            'authentic2/auth2_auth/auth2_oath',
            'authentic2/auth2_auth/auth2_oath/migrations',
            'authentic2/auth2_auth/auth2_openid',
            'authentic2/auth2_auth/auth2_ssl',
            'authentic2/auth2_auth/auth2_ssl/migrations',
            'authentic2/auth2_auth/migrations',
            'authentic2/auth2_auth/templatetags',
            'authentic2/authsaml2',
            'authentic2/authsaml2/migrations',
            'authentic2/idp',
            'authentic2/idp/idp_cas',
            'authentic2/idp/idp_openid',
            'authentic2/idp/idp_openid/migrations',
            'authentic2/idp/idp_openid/templatetags',
            'authentic2/idp/management',
            'authentic2/idp/management/commands',
            'authentic2/idp/migrations',
            'authentic2/idp/saml',
            'authentic2/idp/templatetags',
            'authentic2/locale',
            'authentic2/nonce',
            'authentic2/saml',
            'authentic2/saml/management',
            'authentic2/saml/management/commands',
            'authentic2/saml/migrations',
            'authentic2/vendor',
            'authentic2/vendor/dpam',
            'authentic2/vendor/oath',
            'authentic2/vendor/registration',
            'authentic2/vendor/totp_js',
            ],
      package_data={ '': ['fixtures/*.json',
          'templates/*.html','templates/*/*.html','js/*.js'] },
      data_files=list(ls_r('static', 'share/authentic2/')),
)
