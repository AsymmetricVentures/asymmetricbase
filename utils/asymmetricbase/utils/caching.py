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

from functools import wraps

from django.core.cache import cache

class session_cached_function(object):
	def __init__(self, key, **kwargs):
		self.key = key
		self.timeout = kwargs.get('timeout', 60)
	
	def __call__(self, fn):
		@wraps(fn)
		def wrapped(*args, **kwargs):
			data = cache.get(self.key)
			if data is None:
				data = fn(*args, **kwargs)
				cache.set(self.key, data, self.timeout)
			return data
		return wrapped

class session_cached_property(object):
	def __init__(self, make_key, **kwargs):
		self.make_key = make_key
		self.timeout = kwargs.get('timeout', 300)
	
	def __call__(self, fn):
		self.fn = fn
		return self
	
	def __get__(self, instance, tp = None):
		if instance is None:
			return self
		
		key = self.make_key(instance)
		data = cache.get(key)
		if data is None:
			data = self.fn(instance)
			cache.set(key, data, self.timeout)
		
		return data
			
