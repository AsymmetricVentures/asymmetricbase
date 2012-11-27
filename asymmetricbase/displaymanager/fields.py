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
	def __init__(self, header_name = '', macro_name = ''):
		self.macro_name = macro_name
		super(TemplateField, self).__init__(header_name)
	
	@cached_property
	def template_macro(self):
		return self.model.get_macro(self.macro_name)
	
	def __call__(self, instance):
		return self.template_macro(instance)

class GenericTemplateField(TemplateField):
	"""
	A TemplateField that takes an attr string for resolving attributes of the obj.
	
	It uses a default macro for rendering the obj after resolving all attributes
	in the attr string. This cuts repetition for many cases where the macro only
	serves to resolve attributes. Example:
	
	-macro user_address_phone(obj):
		={ obj.user.address.phone }
	
	can be replaced with a GenericTemplateField that has the default macro and
	attr = 'user.address.phone'
	"""
	def __init__(self, header_name = '', macro_name = 'default', attr = ''):
		self.attr = attr
		super(GenericTemplateField, self).__init__(header_name, macro_name)
	
	def __call__(self, instance):
		return self.template_macro(instance, self.attr)

class AutoTemplateField(TemplateField, AttrGetField):
	
	def __init__(self, *args, **kwargs):
		kwargs['macro_name'] = self.__class__.__name__.lower()
		super(AutoTemplateField, self).__init__(*args, **kwargs)
	
	def __call__(self, instance):
		return TemplateField.__call__(self, AttrGetField.__call__(self, instance))
	
class IntField(AutoTemplateField): pass
class CharField(AutoTemplateField): pass

class GridLayoutField(GenericTemplateField):
	
	def __init__(self, *args, **kwargs):
		self.row = kwargs.pop('row', 0)
		self.col = kwargs.pop('col', 0)
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