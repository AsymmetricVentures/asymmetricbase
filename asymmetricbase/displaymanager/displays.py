from base import Display
import operator
from collections import OrderedDict

class SimpleTableDisplay(Display):
	class Meta(object):
		template_name = ('asymmetricbase/displaymanager/fields.djhtml', 'asymmetricbase/displaymanager/vtable.djhtml')
	
	@property
	def columns(self):
		return self._meta.fields
	
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
		# TODO: efficiency optimization
		# if there's a data structure that can do ordered insert based on the row and col
		# index, this would be more efficient than sorting
		ordered_rows = OrderedDict(sorted(grid.items(), key = operator.itemgetter(0)))
		for row_num, col_dict in ordered_rows.items():
			ordered_rows[row_num] = OrderedDict(sorted(col_dict.items(), key = operator.itemgetter(0)))
		
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
	
	root_field = None
	
	def __init__(self, *args, **kwargs):
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
	class Meta(object):
		template_name = ('asymmetricbase/displaymanager/fields.djhtml', 'asymmetricbase/displaymanager/menu_display.djhtml',)