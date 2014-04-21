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

from django.db import models
from django.utils import timezone
from django.dispatch.dispatcher import receiver
from django.db.models import signals
from django.forms.models import model_to_dict
from django.contrib.contenttypes.models import ContentType

from asymmetricbase.logging import audit_logger
from asymmetricbase.logging.models import LogEntryType, AccessType
from asymmetricbase.fields import UUIDField

class AsymBaseModel(models.Model):
	# The next two lines for for eclipse so that it stops reporting _meta as unknown
	_meta = models.options.Options
	del _meta
	
	
	uuid = UUIDField()
	date_created = models.DateTimeField(auto_now_add = True, default = timezone.now)
	date_updated = models.DateTimeField(auto_now = True, default = timezone.now)
	
	class Meta(object):
		abstract = True
		app_label = 'shared'
	
	def _audit_log(self, access_type, success):
		msg = 'Model Access'
		audit_logger.info(msg, extra = {
			'log_type' : LogEntryType.MODEL,
			'model' : self,
			'access_type' : access_type,
			'success' : success
		})
	
	def _object_saved_before(self):
		''' Returns True if this object has been saved before '''
		return hasattr(self, 'id') and self.id is not None
	
	def __json__(self, encoder):
		return model_to_dict(self, exclude = ['id'])
	
	@classmethod
	def get_content_type(cls):
		return ContentType.objects.get_for_model(cls)

@receiver(signal = signals.post_save, dispatch_uid = 'write_audit_log')
def asym_model_base_postsave(sender, instance, created, raw, using, **kwargs):
	if not isinstance(instance, AsymBaseModel):
		return
	
	if created:
		instance._audit_log(access_type = AccessType.ADD, success = True)
	else:
		instance._audit_log(access_type = AccessType.WRITE, success = True)

@receiver(signal = signals.post_init, dispatch_uid = 'read_permission_check')
def asym_model_base_postinit(sender, instance, **kwargs):
	if not isinstance(instance, AsymBaseModel):
		return
	
	if not instance._object_saved_before():
		return  # this is a constructor call. CanAdd will be checked it in pre_save
	
	instance._audit_log(access_type = AccessType.READ, success = True)
