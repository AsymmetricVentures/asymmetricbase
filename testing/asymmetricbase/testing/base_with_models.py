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

from __future__ import absolute_import, division, print_function, unicode_literals

from django.core.management import call_command
from django.db.models import loading
from django.conf import settings

from .base import BaseTestCase

class BaseTestCaseWithModels(BaseTestCase):
	
	def _pre_setup(self):
		loading.cache.loaded = False
		self._original_installed_apps = list(settings.INSTALLED_APPS)
		settings.INSTALLED_APPS = self._original_installed_apps + ['asymmetricbase.tests', ]
		
		call_command('syncdb', interactive = False, verbosity = 0, migrate = False)
		
		super(BaseTestCaseWithModels, self)._pre_setup()
	
	def _post_teardown(self):
		super(BaseTestCaseWithModels, self)._post_teardown()
		# restore settings
		settings.INSTALLED_APPS = self._original_installed_apps
		loading.cache.loaded = False
