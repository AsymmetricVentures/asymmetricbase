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

__all__ = ('DefaultGroup', 'NamedGroupSet')

from django.contrib.auth.models import Group
from django.db import models

from .base import AsymBaseModel

class NamedGroupSetManager(models.Manager):
	
	def get_groups(self, group_set_identifier):
		return self.get_query_set().get(identifier = group_set_identifier).group_set.all()

class DefaultGroup(AsymBaseModel):
	"""
	Couple a static Group name defined in settings with a Group object.
	
	This allows renaming of the Group while still being able to access it
	by name in the code.
	"""
	identifier = models.IntegerField(unique = True)
	group = models.ForeignKey(Group)

class NamedGroupSet(AsymBaseModel):
	"""
	Couple a set of Group objects with a static name defined in settings.
	"""
	identifier = models.IntegerField()
	group_set = models.ManyToManyField(Group)
	
	objects = NamedGroupSetManager()
