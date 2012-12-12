from django.db import models
from django.core import exceptions
from django.db.models.fields import NOT_PROVIDED
from django.db.models.fields.subclassing import SubfieldBase
from django.utils.text import capfirst
from django.utils.encoding import smart_unicode


from south.modelsinspector import add_introspection_rules

from asymmetricbase.logging import logger # @UnusedImport
from asymmetricbase.utils.enum import Enum, EnumItem
from asymmetricbase import forms

class EnumFormField(forms.TypedChoiceField):
	def prepare_value(self, data):
		if isinstance(data, EnumItem):
			return smart_unicode(data.value)
		
		return data

class EnumField(models.IntegerField):
	__metaclass__ = SubfieldBase
	
	empty_strings_allowed = False
	
	def __init__(self, enum, *args, **kwargs):
		self.enum = enum
		kwargs.update(
			choices = enum.Choices.items(),
			null = False,
			blank = False
		)
		
		super(EnumField, self).__init__(*args, **kwargs)
	
	def get_default(self):
		"""
		Returns the default value for this field.
		
		The default implementation on models.Field calls force_unicode
		on the default, which means you can't set arbitrary Python
		objects as the default. To fix this, we just return the value
		without calling force_unicode on it. Note that if you set a
		callable as a default, the field will still call it.
		
		From: http://djangosnippets.org/snippets/1694/
		
		"""
		if self.has_default():
			default = self.default
			if callable(default):
				default = self.default()
			if default is None:
				return None
			return default.value
		# If the field doesn't have a default, then we punt to models.Field.
		return super(EnumField, self).get_default()
	
	def to_python(self, value):
		if value is None:
			return None
		elif value in self.enum:
			return value
		try:
			return self.enum(int(value))
		except ValueError:
			raise exceptions.ValidationError(self.error_messages['invalid'] % value)
	
	def validate(self, value, model_instance):
		return value in self.enum
	
	def get_prep_value(self, value):
		if value in (None, ''):
			return None
		
		return int(value)
	
	def formfield(self, **kwargs):
		include_blank = (self.blank or not (self.has_default() or 'initial' in kwargs))
		defaults = {
			'required' : not self.blank,
			'label' : self.verbose_name,
			'help_text' : self.help_text,
			'choices': self.get_choices(include_blank = include_blank),
			'coerce': self.to_python,
			'empty_value' : None,
		}
		if self.has_default():
			if callable(self.default):
				defaults['initial'] = self.default
				defaults['show_hidden_initial'] = True
				
			else:
				defaults['initial'] = self.get_default()
		
		for k in kwargs.keys():
			if k not in ('coerce', 'empty_value', 'choices', 'required',
						 'widget', 'label', 'initial', 'help_text',
						 'error_messages', 'show_hidden_initial'):
				del kwargs[k]
		
		defaults.update(**kwargs)
		
		return EnumFormField(**defaults)
		
def enum_converter(value):
	if issubclass(value, Enum):
		return 'Migration().gf("{}.{}")'.format(value.__module__, value.__name__)
	
	raise ValueError("Unknown value type `{!r}` for enum argument".format(value))

def default_converter(value):
	if isinstance(value, NOT_PROVIDED) or value is NOT_PROVIDED:
		return None
	
	elif isinstance(value, EnumItem):
		#return 'getattr(Migration().gf("{}.{}"), "{}")'.format(value._enum_type_.__module__, value._enum_type_.__name__, value._enum_name_)
		return repr(value.value)
	
	raise ValueError(repr(value))

add_introspection_rules(
	[
		(
			[EnumField], # Field Name 
			[], # Args
			{ # kwargs
				'enum' : ['enum', {'converter' : enum_converter, 'is_django_function' : True}],
				'default' : ['default', {'converter' : default_converter, 'is_django_function' : True}],
			}
		)
	],
	['^asymmetricbase\.fields\.enumfield\.EnumField']
)
