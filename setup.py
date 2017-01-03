#!/usr/bin/env python

from distutils.core import setup

PACKAGE_NAME = 'compage'
PACKAGE_VERSION = '1.0.0'

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    description=PACKAGE_NAME,
    author='Alok Gandhi',
    author_email='alok.gandhi2002@gmail.com',
    url='http://www.alokgandhi.net',
    packages=[
        'compage',
    ],
    package_dir={'compage': 'src/compage'},
    )
