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
from datetime import datetime

from django.utils.timezone import utc

class DBLoggingHandler(logging.Handler):
	
	def emit(self, record):
		log_generator = DBLogGenerator(record)
		log_generator.generate()

class DBLogGenerator(object):
	def __init__(self, record):
		self.record = record
	
	def generate(self):
		
		self._save_log_entry()
	
	def _save_log_entry(self):
		
		from django.db import transaction
		from .models import LogEntry
		
		with transaction.commit_on_success():
			LogEntry.objects.create(
				date_created = datetime.fromtimestamp(self.record.created, utc),
				level = self.record.levelno,
				pathname = str(self.record.pathname),
				lineno = self.record.lineno,
				msg = repr(self.record.msg),
				args = repr(self.record.args),
				exc_info = repr(self.record.exc_info),
				func = repr(self.record.funcName)
			)
