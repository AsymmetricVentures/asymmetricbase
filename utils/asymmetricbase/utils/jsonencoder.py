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

import types

from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.query import QuerySet

from .enum import EnumItem

class AsymJSONEncoder(DjangoJSONEncoder):
	
	def default(self, o):
		
		if hasattr(o, '__json__'):
			return o.__json__(self.default)
		if isinstance(o, (QuerySet, set)):
			return list(o)
		elif isinstance(o, (types.FunctionType, types.LambdaType)):
			try:
				from asymmetricbase.logging import logger
				logger.debug("Tried to jsonify a function or lambda")
			except ImportError:
				pass
			return str(o)
		elif isinstance(o, EnumItem):
			return int(o)
		else:
			return super(AsymJSONEncoder, self).default(o)

class AsymJSTreeEncoder(AsymJSONEncoder):
	
	def default(self, o):
		
		if hasattr(o, '__jstree__'):
			return o.__jstree__(self.default)
		else:
			return super(AsymJSTreeEncoder, self).default(o)
