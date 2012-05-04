#! /usr/bin/env python
#
'''
   Setup script for Authentic 2
'''
from setuptools import setup, find_packages
import authentic2


# Build the authentic package.
setup(name="authentic2",
      version=authentic2.VERSION,
      license="AGPLv3 or later",
      description="Authentic 2, a versatile identity management server",
      url="http://dev.entrouvert.org/projects/authentic/",
      author="Entr'ouvert",
      author_email="authentic-devel@lists.labs.libre-entreprise.org",
      maintainer="Benjamin Dauvergne",
      maintainer_email="bdauvergne@entrouvert.com",
      packages=find_packages(),
      include_package_data=True,
)
