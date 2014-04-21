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

from collections import OrderedDict

from .fields import MenuItemField
from .base import Display

class SimpleTableDisplay(Display):
	
	def __init__(self, obj, exclude = (), *args, **kwargs):
		"""
		:param exclude: fields that should not be displayed
		:type exclude: tuble containing field names
		"""
		super(SimpleTableDisplay, self).__init__(obj, *args, **kwargs)
		self.exclude = exclude
	
	class Meta(object):
		template_name = ('asymmetricbase/displaymanager/fields.djhtml', 'asymmetricbase/displaymanager/vtable.djhtml')
	
	@property
	def columns(self):
		return [field for field in self._meta.fields if field.attrname not in self.exclude]
	
	@property
	def items(self):
		return self.obj
	
	@property
	def empty_form(self):
		if hasattr(self.obj, 'empty_form'):
			return self.obj.empty_form
		return None

class GridLayoutDisplay(Display):
	
	_grid = None
	
	class Meta(object):
		template_name = ('asymmetricbase/displaymanager/fields.djhtml', 'asymmetricbase/displaymanager/grid_layout.djhtml',)
	
	def __init__(self, obj, *args, **kwargs):
		super(GridLayoutDisplay, self).__init__(obj, *args, **kwargs)
	
	def _make_grid(self):
		grid = {}
		for field in self._meta.fields:
			if field.row not in grid.keys():
				grid[field.row] = {}
			if field.col not in grid[field.row].keys():
				grid[field.row][field.col] = field
			else:
				raise AttributeError('Grid elements at row {}, col {} already defined.'.format(field.row, field.col))
		# sort rows and columns
		# the sort key is the row and col number, which must be converted to int
		# to avoid lexicographical sort (which places 12 before 2...)
		# TODO: efficiency optimization
		# if there's a data structure that can do ordered insert based on the row and col
		# index, this would be more efficient than sorting
		ordered_rows = OrderedDict(sorted(grid.items(), key = lambda obj: int(obj[0].replace('row-', ''))))
		for row_num, col_dict in ordered_rows.items():
			ordered_rows[row_num] = OrderedDict(sorted(col_dict.items(), key = lambda obj: int(obj[0].replace('col-', ''))))
		
		return ordered_rows
		
	
	@property
	def grid(self):
		# singleton pattern
		if not self._grid:
			self._grid = OrderedDict()
			self._grid = self._make_grid()
		return self._grid
	
	@property
	def item(self):
		return self.obj

class NestedDisplay(Display):
	
	def __init__(self, *args, **kwargs):
		self.root_field = None
		super(NestedDisplay, self).__init__(*args, **kwargs)
		
		# populate children on all fields
		# while we're at it, make sure only one root is defined
		for field in self._meta.fields:
			if getattr(field, 'root', False) and not self.root_field:
				self.root_field = field
			elif getattr(field, 'root', False):
				raise Exception('Only one field should be defined as the root.')
				
			if hasattr(field, 'child') and field.child is None:
				field.child = [attr for attr in self._meta.fields if attr.attrname == field.child_name][0]
	
	class Meta(object):
		template_name = ('asymmetricbase/displaymanager/fields.djhtml', 'asymmetricbase/displaymanager/nested_display.djhtml',)

class MenuDisplay(Display):
	"""
	A Display for rendering a menu using a list of items.
	
	The item_processor attribute should be called on each menu item, and is expecting a MenuItem object as an argument.
	"""
	
	field = MenuItemField()
	
	def __init__(self, *args, **kwargs):
		super(MenuDisplay, self).__init__(*args, **kwargs)
	
	@property
	def item_processor(self):
		# returns 'field' defined above
		# for some reason self.field doesn't exist
		return self._meta.fields[0]
	
	class Meta(object):
		template_name = ('asymmetricbase/displaymanager/fields.djhtml', 'asymmetricbase/displaymanager/menu_display.djhtml',)
