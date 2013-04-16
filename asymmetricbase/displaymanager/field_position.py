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

class FieldPosition(object): pass

class Before(FieldPosition):
	def __init__(self, target, field_type):
		self.target = target
		self.field_type = field_type

class After(FieldPosition):
	def __init__(self, target, field_type):
		self.target = target
		self.field_type = field_type

class Between(FieldPosition):
	def __init__(self, before, after, field_type):
		self.before = before
		self.after = after
		self.field_type = field_type
