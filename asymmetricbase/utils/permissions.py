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

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from .cached_function import cached_function

@cached_function
def default_content_type():
	return ContentType.objects.get_for_model(get_user_model())

def default_content_type_appname():
	return default_content_type().app_label

def create_codename(module_path, cls_name, suffix = ''):
	# Remove the repeated parts of the path
	module_path = module_path.replace('.views', '').replace('project.', '')
	
	# return only the first 100 characters, since that's
	# all that fits in the DB
	return 'view_{}.{}{}'.format(
		module_path,
		cls_name,
		suffix
	)[:100]
