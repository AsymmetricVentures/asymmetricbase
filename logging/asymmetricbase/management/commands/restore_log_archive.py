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

from django.core.management.base import BaseCommand, CommandError
from django.core import serializers
from django.db.transaction import commit_on_success

class Command(BaseCommand):
	
	def _validate_object(self, obj):
		"""
		Return true is object can be saved.
		"""
		cls = obj.object._meta.object_name
		if cls in ['LogEntry', 'AuditEntry', 'TraceEntry']:
			return True
		return False
	
	def handle(self, *args, **options):
		"""
		Restore archived log entries from file. Provide filename as argument.
		"""
		if len(args) != 1:
			raise CommandError("Provide filename as argument.")
		
		filename = args[0]
		
		# restore data
		with commit_on_success():
			with open(filename, 'r') as fp:
				for deserialized_object in serializers.deserialize('json', fp):
					if self._validate_object(deserialized_object):
						deserialized_object.save()
					else:
						raise TypeError("Deserialized object is not LogEntry, TraceEntry, or AuditEntry")
