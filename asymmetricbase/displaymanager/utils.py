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

from jinja2.utils import contextfunction

class ContextAttribute(object):
	
	def __init__(self, attr_name, on_undefined = lambda x:x):
		self.on_undefined = on_undefined
		self.attr_name = attr_name
	
	@contextfunction
	def __call__(self, context, **other_names):
		
		if self.attr_name == '':
			return ''
		
		attrs = self.attr_name.split('.')
		attr_base = attrs.pop(0)
		obj = other_names.get(attr_base, context.environment.getattr(context, attr_base))
		
		for attr in attrs:
			obj = context.environment.getattr(obj, attr)
		
		if not obj:
			return self.on_undefined(obj)
		return obj
		
