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

from asymmetricbase.logging import logger, audit_logger, line_logger

class AddRequestToLoggerMiddleware(object):
	''' Adds the request object to all the loggers.
	This removes the need to store it in a thread global to access it in the
	logging classes'''
	
	def process_request(self, request):
		for l in (logger, audit_logger, line_logger):
			for handler in l.handlers:
				setattr(handler, 'django_request', request)
