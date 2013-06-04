# -*- coding: utf-8 -*-
#    Asymmetric Base Framework - A collection of utilities for django frameworks
#    Copyright (C) 2013  Asymmetric Ventures Inc.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; version 2 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from datetime import datetime
from setuptools import setup

classifiers = """
Development Status :: 4 - Beta
Framework :: Django
Programming Language :: Python
Intended Audience :: Developers
Natural Language :: English
Operating System :: OS Independent
Topic :: Software Development :: Libraries
Topic :: Utilities
License :: OSI Approved :: GNU General Public License v2 (GPLv2)
Topic :: Software Development :: Libraries :: Application Frameworks
"""

setup(
	name = 'asymmetricbase',
	version = datetime.now().strftime('%Y%m%d%H%M'),
	url = 'https://github.com/AsymmetricVentures/asymmetricbase',
	
	author = 'Richard Eames',
	author_email = 'reames@asymmetricventures.com',
	
	packages = (
		'asymmetricbase',
		'asymmetricbase._models',
		'asymmetricbase.displaymanager',
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
		'django(>=1.4.5)',
		'jinja2(==2.7)',
		'pytz',  # most recent
		'south(==0.7.6)',
		'hamlpy',  # most recent,
		'Pillow',
	),
	
	package_dir = {'asymmetricbase' : 'asymmetricbase'},
	package_data = {
		'asymmetricbase' : [
			'templates/asymmetricbase/boundfield/*.djhtml',
			'templates/asymmetricbase/displaymanager/*.djhtml',
			'templates/asymmetricbase/forms/*.djhtml',
		]},
)
