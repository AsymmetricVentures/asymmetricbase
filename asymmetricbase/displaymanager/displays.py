from base import Display

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
	
	def _make_grid(self, grid):
		for field in self._meta.fields:
			if field.row not in grid.keys():
				grid[field.row] = {}
			if field.col not in grid[field.row].keys():
				grid[field.row][field.col] = field
			else:
				raise AttributeError('Grid elements at row {}, col {} already defined.'.format(field.row, field.col))
	
	@property
	def grid(self):
		# singleton pattern
		if not self._grid:
			self._grid = {}
			self._make_grid(self._grid)
		return self._grid
	
	@property
	def item(self):
		return self.obj
