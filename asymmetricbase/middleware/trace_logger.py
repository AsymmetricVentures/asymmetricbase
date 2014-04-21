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

from asymmetricbase.logging import logger, line_logger

class TraceLogger(object):
	
	def _flush(self):
		for handler in logger.handlers:
			if hasattr(handler, 'flush'):
				handler.flush()
	
	def process_request(self, request):
		return None
	
	def process_response(self, request, response):
		self._flush()
		return response
	
	def process_exception(self, request, exception):
		self._flush()
		line_logger.exception('Got exception: {}'.format(exception))
		return None
