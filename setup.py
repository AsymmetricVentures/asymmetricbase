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
	version = '20120712-1',
	
	author = 'Richard Eames',
	author_email = 'reames@asymmetricventures.com',
	
	packages = (
		'asymmetricbase',
		'asymmetricbase.fields',
		'asymmetricbase.forms',
		'asymmetricbase.jinja',
		'asymmetricbase.jinja.tags',
		'asymmetricbase.locale',
		'asymmetricbase.locale.canada',
		'asymmetricbase.locale.canada.forms',
		'asymmetricbase.logging',
		'asymmetricbase.management',
		'asymmetricbase.management.commands',
		'asymmetricbase.middleware',
		'asymmetricbase.migrations',
		'asymmetricbase.pagination',
		'asymmetricbase.testing',
		'asymmetricbase.utils',
		'asymmetricbase.views',
		'asymmetricbase.views.mixins',
	),
	classifiers = filter(None, classifiers.split('\n')),
	
	requires = (
		'django(==1.4)',
		'jinja2(==2.6)',
		'pytz', # most recent
		'south(==0.7.5)'
	),
	
	package_dir = {'asymmetricbase' : 'asymmetricbase'},
	package_data = {
		'asymmetricbase' : [
			'templates/asymmetricbase/boundfield/*.djhtml',
			'templates/asymmetricbase/forms/*.djhtml',
		]},
)
