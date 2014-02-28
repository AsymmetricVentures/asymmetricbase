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

from django.template import TemplateDoesNotExist, loaders

import jinja2

class JinjaLoader(loaders.filesystem.Loader):
	is_usable = True
	
	def load_template(self, template_name, template_dirs = None):
		from . import jinja_env
		
		try:
			template = jinja_env.get_template(template_name)
			return template, template.filename
		except jinja2.TemplateNotFound:
			raise TemplateDoesNotExist(template_name)
