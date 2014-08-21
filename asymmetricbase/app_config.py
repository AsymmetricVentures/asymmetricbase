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

__author__ = "Richard Eames <reames@asymmetricventures.com"
__date__ = "Apr 25, 2014"
__updated__ = "Apr 25, 2014"
__rev__ = "$Id$"

try:
	from django.apps import AppConfig
except ImportError:
	AppConfig = object


class AsymBaseAppConfig(AppConfig):
	name = 'asymmetricbase'
	
	def ready(self):
		from .utils import monkey_patching, monkey_patch_django
		from .jinja import monkey_patching as jinja_monkey
		from .forms import boundfield
		
		monkey_patching.monkey_patch()
		jinja_monkey.monkey_patch_jinja()
		monkey_patch_django.monkey_patch_django()
