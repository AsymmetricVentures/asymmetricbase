#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup

classifiers = """
Development Status :: 3 - Alpha
Framework :: Django
Intended Audience :: Developers
Natural Language :: English
Operating System :: OS Independent
Topic :: Software Development :: Libraries
Topic :: Utilities
"""

setup(
	name = 'asymmetricbase',
	version = '20120503-1',
	
	author = 'Richard Eames',
	author_email = 'reames@asymmetricventures.com',
	
	package = (
		'asymmetricbase',
		'asymmetricbase.jinja',
		'asymmetricbase.logging',
		'asymmetricbase.locale',
		'asymmetricbase.locale.canada',
		'asymmetricbase.locale.canada.forms',
	),
	classifiers = filter(None, classifiers.split('\n')),
	
	requires = (
		'django==1.4',
		'jinja2==2.6',
		'pytz', # most recent
		'south==0.7.4'
	),
	install_requires = (),
)
