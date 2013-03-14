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

import django
from . import monkey_patch_perm_model

def patch_cached_property():
	if cmp(django.VERSION[:3], (1, 5, 0)) < 0:
		# Cached property is broken in django < 1.5
		
		from django.utils.functional import cached_property
		
		def cached_prop__get__(self, instance, type = None): #@ReservedAssignment
			if instance is None:
				return self
			res = instance.__dict__[self.func.__name__] = self.func(instance)
			return res
		
		setattr(cached_property, '__get__', cached_prop__get__)

def monkey_patch():
	patch_cached_property()
	
	# We want longer names in the permission model
	monkey_patch_perm_model.monkey_patch()
	
