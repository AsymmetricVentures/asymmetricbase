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
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

from __future__ import absolute_import, division, print_function, unicode_literals
import warnings

from django.conf import settings
from django.template.context import RequestContext

import jinja2

class UndefinedVar(jinja2.Undefined):
	def __int__(self):
		return 0
	
	def __float__(self):
		return 0.0
	
	def __str__(self):
		return self.__html__()
	
	def __iter__(self):
		class EmptyIter(object):
			def __iter__(self):
				return self
			def next(self): # @ReservedAssignment
				raise StopIteration()
			
		return EmptyIter()
		
	def __html__(self):
		return u'%NONE%'
	
	def __getattribute__(self, name, *args, **kwargs):
			
		try:
			return super(UndefinedVar, self).__getattribute__(name, *args, **kwargs)
		except AttributeError:
			if settings.TEMPLATE_DEBUG:
				import inspect
				f = inspect.currentframe().f_back.f_back.f_code
				file_name = f.co_filename
				lineno = f.co_firstlineno
				warnings.warn("[{}:{}] Trying to access attribute '{}' on undefined variable '{}'".format(file_name, lineno, name, self._undefined_name))
			return UndefinedVar()
		
		return None

class JinjaTemplate(jinja2.Template):
	
	def render(self, *args, **kwargs):
		ctx = {}
		if len(args) == 1 and len(kwargs) == 0 and isinstance(args[0], RequestContext):
			ctx = JinjaEnvironment.context_to_dict(args[0])
		else:
			ctx.update(*args, **kwargs)
		
		return super(JinjaTemplate, self).render(ctx)
				

class JinjaEnvironment(jinja2.Environment):
	
	def __init__(self, *args, **kwargs):
		super(JinjaEnvironment, self).__init__(*args, **kwargs)
		
		self.template_class = JinjaTemplate
	
	def get_template_module(self, template_name, ctx = None):
		return self.get_template(template_name).make_module(vars = ctx)
	
	@classmethod
	def context_to_dict(cls, ctx):
		merged_context = {}

		for d in reversed(ctx.dicts):
			merged_context.update(d)
		
		return merged_context
	
