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

import sys

from django.utils import timezone

class MonthIter(object):
	def __init__(self, start_date, end_date = None, months = 1):
		self.start_date = start_date.replace(day = 1)
		self.end_date = timezone.now().replace(day = 1) if end_date is None else end_date.replace(day = 1)
		self.months = months
		self.current = self.start_date
		
	def __iter__(self):
		return self
	
	def __next__(self):
		if self.current <= self.end_date:
			ret = self.current
			carry, new_month = divmod(self.current.month - 1 + self.months, 12)
			new_month += 1
			self.current = self.current.replace(year = self.current.year + carry, month = new_month)
			return ret 
		else:
			raise StopIteration()
	

if sys.version_info < (3, 0):
	MonthIter.next = MonthIter.__next__
