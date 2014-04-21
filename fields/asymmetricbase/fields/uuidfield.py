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

import uuid

from django.db import models
from django.db.utils import IntegrityError

class UUIDField(models.CharField):
	
	def __init__(self, *args, **kwargs):
		kwargs['max_length'] = 40
		kwargs['blank'] = True
		kwargs['db_index'] = True
		self.auto_add = kwargs.pop('auto_add', True)
		
		super(UUIDField, self).__init__(*args, **kwargs)
	
	def pre_save(self, model_instance, add):
		if (self.auto_add and add):
			kls = model_instance.__class__
			for _ in range(100):
				new_uuid = uuid.uuid4().hex[0:10]
				if not kls.objects.filter(uuid = new_uuid).exists():
					setattr(model_instance, self.attname, new_uuid)
					return new_uuid
			raise IntegrityError('Unable to generate a unique uuid for model: {}'.format(kls))
		
		else:
			return super(UUIDField, self).pre_save(model_instance, add)

try:
	from south.modelsinspector import add_introspection_rules
	
	add_introspection_rules([], ['^asymmetricbase\.fields\.uuidfield\.UUIDField'])
except ImportError:
	pass
