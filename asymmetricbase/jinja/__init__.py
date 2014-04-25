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

from django.conf import settings
from django.utils.functional import lazy, SimpleLazyObject
import jinja2
from jinja2.ext import WithExtension, LoopControlExtension

from asymmetricbase.jinja.tags.csrf_token import CSRFTokenExtension

from . import filters, global_functions, environment
from .monkey_patching import monkey_patch_jinja

def get_jinja_env():
	from django.template.loaders.app_directories import	app_template_dirs
	template_loader = getattr(settings, 'ASYM_TEMPLATE_LOADER', jinja2.FileSystemLoader(app_template_dirs))

	if callable(template_loader):
		template_loader = template_loader()
	return template_loader

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
	
	jinja_env.globals.update(global_functions.get_functions(jinja_env))
	
	jinja_env.filters.update(filters.get_filters(jinja_env))

jinja_env = get_jinja_env()