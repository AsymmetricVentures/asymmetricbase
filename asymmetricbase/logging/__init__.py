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

import logging

from django.utils.functional import SimpleLazyObject

class NullHandler(logging.Handler):
	def emit(self, record):
		pass

def init_logger():
	from django.conf import settings
	logger_name = getattr(settings, 'ASYM_LOGGER', 'asymm_logger')
	
	_logger = logging.getLogger(logger_name)
	_logger.addHandler(NullHandler())
	return _logger

def init_audit_logger():
	from django.conf import settings
	logger_name = getattr(settings, 'ASYM_AUDIT_LOGGER', 'asymm_audit_logger')
	
	_logger = logging.getLogger(logger_name)
	_logger.addHandler(NullHandler())
	return _logger

def init_tracing_logger():
	from django.conf import settings
	logger_name = getattr(settings, 'ASYM_TRACE_LOGGER', 'asymm_trace_logger')
	
	_logger = logging.getLogger(logger_name)
	_logger.addHandler(NullHandler())
	return _logger

logger = SimpleLazyObject(init_tracing_logger)
line_logger = SimpleLazyObject(init_logger)
audit_logger = SimpleLazyObject(init_audit_logger)
