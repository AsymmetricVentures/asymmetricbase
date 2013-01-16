from functools import total_ordering
from django.utils.functional import cached_property

@total_ordering
class DisplayField(object):
	creation_counter = 0
	
	def __init__(self, header_name = None):
		self.header_name = header_name
		self.attrname = ''
		self.model = None
		
		self.creation_counter = DisplayField.creation_counter
		DisplayField.creation_counter += 1
	
	def contribute_to_class(self, cls, name):
		self.attrname = name
		self.model = cls
		
		if self.header_name is None:
			self.header_name = name.replace('_', ' ').title()
		
		if hasattr(cls, '_meta'):
			cls._meta.add_field(self)
	
	def __str__(self):
		return str(getattr(self.model, self.name))
	
	def __eq__(self, other):
		return self.creation_counter == other.creation_counter
	
	def __lt__(self, other):
		return self.creation_counter < other.creation_counter

class AttrGetField(DisplayField):
	''' Can be used in 1 of two ways
	    First, in a display of the form:
	      attr_name = dm.AttrGetField()
	    will display `obj.attr_name`
	    
	    Second, in a display of the form:
	      name = dm.AttrGetField(attr='nested.attribute')
	    will display `obj.nested.attribute`
	'''
	def __init__(self, header_name = None, attr = None):
		super(AttrGetField, self).__init__(header_name)
		self.attr = attr 
	
	def __call__(self, instance):
		return self.attr_field_macro(instance, attr = self.field_name)
	
	@cached_property
	def attr_field_macro(self):
		return self.model.get_macro('attr_field')
	
	@property
	def field_name(self):
		return self.attr if self.attr is not None else self.attrname

class TemplateField(DisplayField):
	"""
	Renders using the macro defined in macro_name.
	
	Can be given additional positional or keyword arguments, which will be passed
	to the macro if the macro supports varargs or kwargs (see jinja2 docs).
	"""
	def __init__(self, header_name = None, macro_name = '', *args, **kwargs):
		self.macro_name = macro_name
		self.args = args
		self.kwargs = kwargs
		super(TemplateField, self).__init__(header_name)
	
	@cached_property
	def template_macro(self):
		return self.model.get_macro(self.macro_name)
	
	def __call__(self, instance):
		return self.template_macro(instance, *self.args, **self.kwargs)

class AutoTemplateField(TemplateField, AttrGetField):
	
	def __init__(self, *args, **kwargs):
		kwargs['macro_name'] = self.__class__.__name__.lower()
		super(AutoTemplateField, self).__init__(*args, **kwargs)
	
	def __call__(self, instance):
		return TemplateField.__call__(self, AttrGetField.__call__(self, instance))

class LinkField(AutoTemplateField):
	'''
	'''
	def __init__(self, header_name = None, url_name = '', *args, **kwargs):
		macro_name = kwargs.pop('macro_name', None)
		self.url_name = url_name
		super(LinkField, self).__init__(*args, **kwargs)
		
		if macro_name is not None:
			self.macro_name = macro_name
	
	def __call__(self, instance):
		return self.template_macro(AttrGetField.__call__(self, instance), self.url_name, *self.args, **self.kwargs)

class IntField(AutoTemplateField): pass
class CharField(AutoTemplateField): pass

class GridLayoutField(TemplateField):
	
	def __init__(self, *args, **kwargs):
		self.row = 'row-' + str(kwargs.pop('row', 0))
		self.col = 'col-' + str(kwargs.pop('col', 0))
		self.rowspan = kwargs.pop('rowspan', 1)
		self.colspan = kwargs.pop('colspan', 1)
		super(GridLayoutField, self).__init__(*args, **kwargs)

class NestedTemplateField(TemplateField):
	
	def __init__(self, header_name = None, macro_name = '', child_name = None, root = False, *args, **kwargs):
		self.child_name = child_name
		self.child = None
		self.root = root
		
		super(NestedTemplateField, self).__init__(header_name, macro_name, *args, **kwargs)
	
	def __call__(self, instance):
		return self.template_macro(instance, self.child, *self.args, **self.kwargs)

class MenuItemField(TemplateField):
	
	def __init__(self, header_name = '', macro_name = 'linkfield', *args, **kwargs):
		super(MenuItemField, self).__init__(header_name, macro_name, *args, **kwargs)
	
	def __call__(self, instance):
		if not isinstance(instance, MenuItem):
			raise TypeError('MenuItemField must be called on an instance of MenuItem')
		kwargs = {}
		kwargs['url_kwargs'] = instance.kwargs
		kwargs['url_args'] = instance.args
		kwargs['url_text'] = instance.label
		kwargs['get_args'] = instance.url_args
		return self.template_macro(instance, url_name = instance.url, **kwargs)

class MenuItem(object):
	"""
	Encapsulates a menu item for use with MenuDisplay.
	
	If the args or kwargs cannot be resolved now (IE we need to wait on a form or callback)
	pass them in wrapped in lambda functions, as they can be resolved using
	process_arguments() later.
	"""
	
	def __init__(self, url = None, label = '', url_args = None, *args, **kwargs):
		self.url = url
		self.label = label
		self.url_args = url_args
		self.args = args
		self.kwargs = kwargs
	
	def process_arguments(self):
		"""
		Check if any argument in self.args or self.kwargs is callable
		(IE lambda functions) and call any that are.
		"""
		
		new_args = []
		for arg in self.args:
			if callable(arg):
				new_args.append(arg())
			else:
				new_args.append(arg)
		self.args = tuple(new_args)
		
		for k, v in self.kwargs.items():
			if callable(v):
				v = v()
			self.kwargs.update({
				k : v
			})
		
		if callable(self.url_args):
			self.url_args = self.url_args()
