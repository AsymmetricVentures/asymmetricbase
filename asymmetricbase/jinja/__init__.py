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

from django.conf import settings
from django.utils.functional import lazy, SimpleLazyObject
import jinja2
from jinja2.ext import WithExtension, LoopControlExtension

from .tags.csrf_token import CSRFTokenExtension
from . import filters, global_functions, environment

def get_jinja_env(self):
	from django.template.loaders.app_directories import	app_template_dirs
	template_loader = getattr(settings, 'ASYM_TEMPLATE_LOADER', jinja2.FileSystemLoader(app_template_dirs))
	
	if hasattr(template_loader, '__call__'):
		template_loader = template_loader()
	
	jinja_env = environment.JinjaEnvironment(
		loader = template_loader,
		undefined = environment.UndefinedVar,
		autoescape = True,
		extensions = [
			CSRFTokenExtension,
			WithExtension,
			LoopControlExtension
		],
	)
	assert isinstance(jinja_env.globals, dict)
	jinja_env.globals.update(global_functions.get_functions(jinja_env))
	jinja_env.filters.update(filters.get_filters(jinja_env))
	
	return jinja_env

jinja_env = SimpleLazyObject(get_jinja_env)

default_app_config = 'asymmetricbase.jinja.app_config.JinjaAppConfig'

if django.get_version() < '1.7':
	from .app_config import JinjaAppConfig
	JinjaAppConfig.ready()
