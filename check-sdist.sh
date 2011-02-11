#!/bin/bash

VERSION=`cat authentic2/__init__.py | grep VERSION | sed 's/VERSION = "\(.*\)"/\1/'`


rm -f dist/authentic2-$VERSION.tar.gz && \
python setup.py sdist && \
diff <(git ls-files|sort) <(tar tf dist/authentic2-$VERSION.tar.gz|sort|grep -v '/$'|sed "s#.*-$VERSION/##")
