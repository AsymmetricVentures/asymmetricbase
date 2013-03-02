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

from django.db import models
from django.utils import timezone

from asymmetricbase.utils.enum import Enum

class LogEntryType(Enum):
	MODEL = 1, 'model'
	VIEW = 2, 'view'
	LOGIN = 3, 'login'
	ASSIGN = 4, 'assign'
	OTHER = 5, 'other'

class AccessType(Enum):
	READ = 1, 'read'
	WRITE = 2, 'write'
	ADD = 3, 'add'
	GRANT = 4, 'grant'
	ASSIGN = 5, 'assign'
	UNASSIGN = 6, 'unassign'
	VIEW = 7, 'view'
	OTHER = 8, 'other'

class ObjectContent(models.Model):
	time_stamp = models.DateTimeField('action time', auto_now = True, default = timezone.now)
	content_in_json = models.TextField('Object Content in JSON format')
	
	class Meta(object):
		app_label = 'asymmetricbase'
	
	def __unicode__(self):
		return u'content_in_json: {self.content_in_json} '.format(self = self)
	
	def get_original_object(self):
		from django.core import serializers
		obj = list(serializers.deserialize("json", self.content_in_json))[0].object
		return obj
	
class AuditEntry(models.Model):
	log_type = models.CharField(max_length = 10, choices = LogEntryType.Choices.items())
	access_type = models.CharField(max_length = 10, choices = AccessType.Choices.items())
	time_stamp = models.DateTimeField('Time Stamp', auto_now = True, default = timezone.now)
	user_id = models.IntegerField('UserBase.ID', null = True, blank = True)
	ip = models.IPAddressField("Origin IP")	
	message = models.TextField('change message', blank = True)
	model_name = models.CharField('for LogEntryType == MODEL', max_length = 256, null = True, blank = True)
	view_name = models.CharField('for LogEntryType == VIEW', max_length = 256, null = True, blank = True)
	success = models.NullBooleanField(null = True)
	object_content = models.ForeignKey(ObjectContent, null = True)
	
	class Meta(object):
		ordering = ('time_stamp',)
		app_label = 'asymmetricbase'
		
	def __unicode__(self):
		return u"""Time: {time_stamp}
IP: {ip}
User-ID: {user_id}
Log Type: {log_type}
Access Type: {access_type}
Model Name: {model_name}
View Name: {view_name}
Success: {success}
Message: {message}
Object Content: {object_content}""".format(
			time_stamp = self.time_stamp,
			ip = self.ip,
			user_id = self.user_id,
			log_type = LogEntryType.Choices[self.log_type],
			access_type = AccessType.Choices[self.access_type],
			model_name = self.model_name,
			view_name = self.view_name,
			success = self.success,
			message = self.message,
			object_content = self.object_content
		)

class LogEntry(models.Model):
	date_created = models.DateTimeField(default = timezone.now)
	level = models.IntegerField()
	pathname = models.CharField(max_length = 255)
	lineno = models.IntegerField()
	msg = models.TextField(blank = True)
	args = models.TextField(blank = True)
	exc_info = models.TextField(blank = True)
	func = models.TextField(blank = True)
	
	class Meta(object):
		app_label = 'asymmetricbase'

class TraceEntry(models.Model):
	date_created = models.DateTimeField(default = timezone.now)
	get = models.TextField(blank = True)
	msg = models.TextField(blank = True)
	exc_info = models.TextField(blank = True)
	
	method = models.CharField(blank = True, default = '', max_length = 10)
	user = models.CharField(blank = True, default = '', max_length = 100)
	request_meta = models.TextField(blank = True, default = '')
	request_data = models.TextField(blank = True, default = '') # Either POST or GET
	
	class Meta(object):
		app_label = 'asymmetricbase'
	
