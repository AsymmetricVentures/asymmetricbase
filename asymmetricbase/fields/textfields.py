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

from south.modelsinspector import add_introspection_rules

from asymmetricbase.logging import logger # @UnusedImport

'''
This file adds model fields for character fields of various lengths
'''

SHORT_MESSAGE_LENGTH = 140
LONG_MESSAGE_LENGTH = 255
SHORT_NAME_LENGTH = 50
LONG_NAME_LENGTH = (SHORT_MESSAGE_LENGTH * 2) + 5

COMMENT_LENGTH = 1024

class ShortMessageField(models.CharField):
	def __init__(self, *args, **kwargs):
		kwargs.setdefault('max_length', SHORT_MESSAGE_LENGTH)
		super(ShortMessageField, self).__init__(*args, **kwargs)

class LongMessageField(models.CharField):
	def __init__(self, *args, **kwargs):
		kwargs.setdefault('max_length', LONG_MESSAGE_LENGTH)
		super(LongMessageField, self).__init__(*args, **kwargs)

class ShortNameField(models.CharField):
	def __init__(self, *args, **kwargs):
		kwargs.setdefault('max_length', SHORT_NAME_LENGTH)
		super(ShortNameField, self).__init__(*args, **kwargs)

class LongNameField(models.CharField):
	def __init__(self, *args, **kwargs):
		kwargs.setdefault('max_length', LONG_NAME_LENGTH)
		super(LongNameField, self).__init__(*args, **kwargs)

class CommentField(models.CharField):
	def __init__(self, *args, **kwargs):
		kwargs.setdefault('max_length', COMMENT_LENGTH)
		super(CommentField, self).__init__(*args, **kwargs)

add_introspection_rules([], [
	'^asymmetricbase\.fields\.textfields\.ShortMessageField',
	'^asymmetricbase\.fields\.textfields\.LongMessageField',
	'^asymmetricbase\.fields\.textfields\.ShortNameField',
	'^asymmetricbase\.fields\.textfields\.LongNameField',
	'^asymmetricbase\.fields\.textfields\.CommentField',
])
