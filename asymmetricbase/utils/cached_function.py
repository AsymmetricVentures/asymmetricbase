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

def cached_function(func):
	"""
	Wrap a function so that it always returns the same thing, but only executes
	its code once.
	
	Similar to django's "cached_property"
	
	Note: Assumes that the function will be called with the same arguments each time
	
	>>> def myfunc():
	...   print("HELLO")
	...   return 42
	>>> f = cached_function(myfunc)
	>>> myfunc()
	HELLO
	42
	>>> myfunc()
	HELLO
	42
	>>> f()
	HELLO
	42
	>>> f()
	42
	
	"""
	
	@wraps(func)
	def wrapper(*args, **kwargs):
		if not hasattr(func, '__cached_result__'):
			func.__cached_result__ = func(*args, **kwargs)
		
		return func.__cached_result__
	
	return wrapper
		

