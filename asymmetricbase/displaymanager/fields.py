from functools import total_ordering
from django.utils.functional import cached_property

@total_ordering
class DisplayField(object):
	creation_counter = 0
	
	def __init__(self, header_name = ''):
		self.header_name = header_name
		self.attrname = ''
		self.model = None
		
		self.creation_counter = DisplayField.creation_counter
		DisplayField.creation_counter += 1
	
	def contribute_to_class(self, cls, name):
		self.attrname = name
		self.model = cls
		if hasattr(cls, '_meta'):
			cls._meta.add_field(self)
	
	def __str__(self):
		return str(getattr(self.model, self.name))
	
	def __eq__(self, other):
		return self.creation_counter == other.creation_counter
	
	def __lt__(self, other):
		return self.creation_counter < other.creation_counter

class AttrGetField(DisplayField):
	def __init__(self, header_name = '', attr = None):
		super(AttrGetField, self).__init__(header_name)
		self.attr = attr 
	
	def __call__(self, instance):
		return getattr(instance, self.field_name)
	
	@property
	def field_name(self):
		return self.attr if self.attr is not None else self.attrname

class TemplateField(DisplayField):
	"""
	Renders using the macro defined in macro_name.
	
	Can be given additional positional or keyword arguments, which will be passed
	to the macro if the macro supports varargs or kwargs (see jinja2 docs).
	"""
	def __init__(self, header_name = '', macro_name = 'default', *args, **kwargs):
		self.macro_name = macro_name
		self.args = args
		self.kwargs = kwargs
		super(TemplateField, self).__init__(header_name)
	
	@cached_property
	def template_macro(self):
		return self.model.get_macro(self.macro_name)
	
	def __call__(self, instance):
		if self.template_macro.catch_varargs and self.template_macro.catch_kwargs:
			return self.template_macro(instance, *self.args, **self.kwargs)
		elif self.template_macro.catch_varargs:
			return self.template_macro(instance, *self.args)
		elif self.template_macro.catch_kwargs:
			return self.template_macro(instance, **self.kwargs)
		else:
			return self.template_macro(instance)

class AutoTemplateField(TemplateField, AttrGetField):
	
	def __init__(self, *args, **kwargs):
		kwargs['macro_name'] = self.__class__.__name__.lower()
		super(AutoTemplateField, self).__init__(*args, **kwargs)
	
	def __call__(self, instance):
		return TemplateField.__call__(self, AttrGetField.__call__(self, instance))
	
class IntField(AutoTemplateField): pass
class CharField(AutoTemplateField): pass

class GridLayoutField(TemplateField):
	
	def __init__(self, *args, **kwargs):
		self.element_attrs = kwargs.pop
		self.row = 'row-' + str(kwargs.pop('row', 0))
		self.col = 'col-' + str(kwargs.pop('col', 0))
		self.rowspan = kwargs.pop('rowspan', 1)
		self.colspan = kwargs.pop('colspan', 1)
		super(GridLayoutField, self).__init__(*args, **kwargs)

class VsegGridLayoutField(GridLayoutField):
	"""
	Like GridLayoutField, but the attr string is concatenated with '.vseg' to
	ease form field rendering.
	"""
	def __init__(self, *args, **kwargs):
		attr = kwargs.get('attr', None)
		if attr:
			attr = attr + '.vseg'
			kwargs['attr'] = attr
		super(VsegGridLayoutField, self).__init__(*args, **kwargs)