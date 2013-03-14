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

from jinja2.nodes import _context_function_types


def is_special_function(fn):
	return hasattr(fn, 'contextfunction') or hasattr(fn, 'evalcontextfunction') or hasattr(fn, 'environmentfunction')

def Context_call(__self, __obj, *args, **kwargs):
	"""Call the callable with the arguments and keyword arguments
	provided but inject the active context or environment as first
	argument if the callable is a :func:`contextfunction` or
	:func:`environmentfunction`.
	"""
	if __debug__:
		__traceback_hide__ = True
	
	if hasattr(__obj, '__call__') and is_special_function(__obj.__call__):
		__obj = getattr(__obj, '__call__')
		
	if isinstance(__obj, _context_function_types):
		if getattr(__obj, 'contextfunction', 0):
			args = (__self,) + args
		elif getattr(__obj, 'evalcontextfunction', 0):
			args = (__self.eval_ctx,) + args
		elif getattr(__obj, 'environmentfunction', 0):
			args = (__self.environment,) + args
	try:
		return __obj(*args, **kwargs)
	except StopIteration:
		return __self.environment.undefined('value was undefined because '
											'a callable raised a '
											'StopIteration exception')

def patch_conditional_escape():
	from django.utils import html as django_html_utils
	
	from jinja2._markupsafe import Markup
	
	old_conditional_escape = django_html_utils.conditional_escape
	def conditional_escape(html):
		"""
		Override django's conditional_escape to look for jinja's MarkupSafe
		"""
		if isinstance(html, Markup):
			return html
		else:
			return old_conditional_escape(html)
		
	setattr(django_html_utils, 'conditional_escape', conditional_escape)

def monkey_patch_jinja():
	from jinja2.runtime import Context
	# Ugly hack to enable calling classes with @contextfunction
	setattr(Context, 'call', Context_call)
	
	patch_conditional_escape()
