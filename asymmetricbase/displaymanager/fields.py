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
	

class AutoTemplateField(TemplateField, AttrGetField):
	
	def __init__(self, *args, **kwargs):
		kwargs['macro_name'] = self.__class__.__name__.lower()
		super(AutoTemplateField, self).__init__(*args, **kwargs)
	
	def __call__(self, instance):
		return TemplateField.__call__(self, AttrGetField.__call__(self, instance))
	
class IntField(AutoTemplateField): pass
class CharField(AutoTemplateField): pass
