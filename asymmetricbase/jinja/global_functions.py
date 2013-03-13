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

from django.utils import timezone
from django.core.urlresolvers import reverse

from jinja2.utils import contextfunction

from . import environment

# TODO: this needs to be removed, and jinja_getattr needs a work around.
dummy_env = environment.JinjaEnvironment(undefined = environment.UndefinedVar)

def jinja_url(view_name, *args, **kwargs):
	return reverse(view_name, args = args, kwargs = kwargs)

def jinja_getdate():
	return timezone.localtime(timezone.now())

def jinja_getattr(obj, attr_string):
	"""
	Resolve attributes using jinja's getattr() rather than the default python method.
	
	Will also resolve chained attributes, for example:
	
		getattr(obj, 'user.name')
		
	will resolve obj.user.name
	"""
	if attr_string == '':
		return obj
	attrs = attr_string.split(".")
	for attr in attrs:
		obj = dummy_env.getattr(obj, attr)
	return obj


@contextfunction
def jinja_context_getattr(context, attr_string):
	"""
	Tries to get attribute by name from context
	"""
	return jinja_getattr(context, attr_string)

@contextfunction
def jinja_batch_context_getattr(context, *args, **kwargs):
	new_args = []
	new_kwargs = {}
	if args:
		for arg in args:
			new_args.append(jinja_context_getattr(context, arg))
		return new_args
	if kwargs:
		for k, v in kwargs.items():
			new_kwargs[k] = jinja_context_getattr(context, v)
		return new_kwargs

@contextfunction
def jinja_vtable(ctx, table, header = '', tail = ''):
	return ctx.environment.get_template_module('asymmetricbase/displaymanager/base.djhtml', ctx).vtable(table, header, tail)

@contextfunction
def jinja_gridlayout(ctx, layout):
	return ctx.environment.get_template_module('asymmetricbase/displaymanager/base.djhtml', ctx).gridlayout(layout)

@contextfunction
def jinja_display(ctx, layout):
	return ctx.environment.get_template_module('asymmetricbase/displaymanager/base.djhtml', ctx).display(layout)

def get_functions():
	return {
		'url' : jinja_url,
		'getdatetime' : jinja_getdate,
		'type' : type,
		'dir' : dir,
		'getattr' : jinja_getattr,
		'context_getattr' : jinja_context_getattr,
		'batch_context_getattr' : jinja_batch_context_getattr,
		
		
		'vtable' : jinja_vtable,
		'gridlayout' : jinja_gridlayout,
		'display' : jinja_display,
	}
