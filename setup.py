#!/usr/bin/env python

from distutils.core import setup

PACKAGE_NAME = 'compage'
PACKAAGE_VERSION = '0.0.1'

setup(
    name=PACKAGE_NAME,
    version=PACKAAGE_VERSION,
    description=PACKAGE_NAME,
    author='Alok Gandhi',
    author_email='alok.gandhi2002@gmail.com',
    url='http://www.alokgandhi.net',
    packages=['compage'],
    package_dir={'compage': 'src/compage'},
    )
