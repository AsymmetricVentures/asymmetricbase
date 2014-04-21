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

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.core import serializers
from django.db.transaction import commit_on_success

class Command(BaseCommand):
	
	def handle(self, *args, **options):
		"""
		Archive old log entries. Provide path as first argument to change
		location of output file.
		"""
		from asymmetricbase.logging.models import LogEntry, TraceEntry, AuditEntry
		
		path = args[0] if len(args) > 0 else './'
		
		keep_days = getattr(settings, 'ASYM_KEEP_LOGS', 4) # only keep 4 days worth
		cutoff = timezone.now() - timedelta(days = keep_days)
		JSONSerializer = serializers.get_serializer('json')
		json_serializer = JSONSerializer()
		
		# get filename prefixes
		logs_prefix = getattr(settings, 'ASYM_LOGENTRY_ARCHIVE_FILE_PREFIX', 'log')
		traces_prefix = getattr(settings, 'ASYM_TRACEENTRY_ARCHIVE_FILE_PREFIX', 'trace')
		audits_prefix = getattr(settings, 'ASYM_AUDITENTRY_ARCHIVE_FILE_PREFIX', 'audit')
		
		# get querysets for each log type
		logs = LogEntry.objects.filter(date_created__lt = cutoff)
		traces = TraceEntry.objects.filter(date_created__lt = cutoff)
		audits = AuditEntry.objects.filter(time_stamp__lt = cutoff)
		
		# combine into list
		to_archive = [
			{'prefix': logs_prefix, 'qs': logs},
			{'prefix': traces_prefix, 'qs': traces},
			{'prefix': audits_prefix, 'qs': audits},
		]
		
		with commit_on_success():
			for parms in to_archive:
				# write objects to file
				filename = '{}{}_archive_{}_keep_{}_days.json'.format(
					path,
					parms['prefix'],
					timezone.now(),
					keep_days,
				)
				with open(filename, 'w') as out:
					json_serializer.serialize(parms['qs'], stream = out)
				
				# delete objects from DB
				parms['qs'].delete()
