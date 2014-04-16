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

import django
from . import monkey_patch_django_auth_models

def patch_cached_property():
	if django.get_version() < '1.5':
		# Cached property is broken in django < 1.5
		
		from django.utils.functional import cached_property
		
		def cached_prop__get__(self, instance, type = None): #@ReservedAssignment
			if instance is None:
				return self
			res = instance.__dict__[self.func.__name__] = self.func(instance)
			return res
		
		setattr(cached_property, '__get__', cached_prop__get__)

def patch_email_field_length():
	from django.db.models.fields import EmailField
	def emailfield__init__(self, *args, **kwargs):
		kwargs['max_length'] = kwargs.get('max_length', 254) # 254 chars == compliant with RFCs 3696 and 5321
		super(EmailField, self).__init__(*args, **kwargs)
	
	setattr(EmailField, '__init__', emailfield__init__)

def monkey_patch():
	patch_cached_property()
	
	# We want longer names in the permission model
	monkey_patch_django_auth_models.monkey_patch()
	
	# Create compliant email fields
	patch_email_field_length()
	
