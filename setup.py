#! /usr/bin/env python
#
# Setup script for Authentic
#
# It started as a copy of ReviewBoard setup.py file, thanks to them, and for
# the record they themselves gave a big thanks to Django project for some of
# the fixes used in here for MacOS X and data files installation.

import os
import shutil
import sys

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
from distutils.command.install_data import install_data
from distutils.command.install import INSTALL_SCHEMES


# Make sure we're actually in the directory containing setup.py.
root_dir = os.path.dirname(__file__)

if root_dir != "":
    os.chdir(root_dir)


# Tell distutils to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']


class osx_install_data(install_data):
    # On MacOS, the platform-specific lib dir is
    # /System/Library/Framework/Python/.../
    # which is wrong. Python 2.5 supplied with MacOS 10.5 has an
    # Apple-specific fix for this in distutils.command.install_data#306. It
    # fixes install_lib but not install_data, which is why we roll our own
    # install_data class.

    def finalize_options(self):
        # By the time finalize_options is called, install.install_lib is
        # set to the fixed directory, so we set the installdir to install_lib.
        # The # install_data class uses ('install_data', 'install_dir') instead.
        self.set_undefined_options('install', ('install_lib', 'install_dir'))
        install_data.finalize_options(self)


if sys.platform == "darwin":
    cmdclasses = {'install_data': osx_install_data}
else:
    cmdclasses = {'install_data': install_data}

# We only want to do this if it's not an sdist build, which means there will
# be a PKG-INFO.
if not os.path.exists("PKG-INFO"):
    if os.path.exists("authentic"):
        shutil.rmtree("authentic")

    print "Copying tree to staging area..."
    shutil.copytree(".", "authentic", True)

    # Clean up things that shouldn't be in there...
    shutil.rmtree("authentic/Authentic.egg-info", ignore_errors=True)
    shutil.rmtree("authentic/build", ignore_errors=True)
    shutil.rmtree("authentic/dist", ignore_errors=True)
    os.unlink("authentic/setup.py")
    os.unlink("authentic/ez_setup.py")

    if os.path.exists("authentic/local_settings.py"):
        os.unlink("authentic/local_settings.py")

    if os.path.exists("authentic/local_settings.pyc"):
        os.unlink("authentic/local_settings.pyc")

# Since we don't actually keep our directories in a authentic directory
# like we really should, we have to fake it. Prepend "authentic." here,
# set package_dir below.
authentic_dirs = []

for dirname in os.listdir("."):
    if os.path.isdir(dirname) and dirname != 'authentic':
        authentic_dirs.append(dirname)
        authentic_dirs.append(dirname + ".*")

packages = [ package_name for package_name in find_packages(exclude=authentic_dirs) ]

# Import this now, since authentic is in the right place now.
from authentic import VERSION

# Build the authentic package.
setup(name="authentic",
      version=VERSION,
      license="GPLv2 or later",
      description="Authentic, a versatile identity server",
      url="http://authentic.labs.libre-entreprise.org/",
      author="Entr'ouvert",
      author_email="authentic-devel@lists.labs.libre-entreprise.org",
      maintainer="Benjamin Dauvergne",
      maintainer_email="bdauvergne@entrouvert.com",
      packages=packages,
      cmdclass=cmdclasses,
      install_requires=[
          'Django>=1.2.0',
          'django-registration',
      ],
      include_package_data=True,
      zip_safe=False,
      classifiers=[
          "Development Status :: 2 - Pre-Alpha",
          "Environment :: Web Environment",
          "Framework :: Django",
          "Intended Audience :: System Administrators",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: System :: Systems Administration :: Authentication/Directory",
      ]
)

if not os.path.exists("PKG-INFO"):
    shutil.rmtree("authentic")
