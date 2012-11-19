from django.db import models
from django.core import exceptions
from django.db.models.fields import NOT_PROVIDED
from django.db.models.fields.subclassing import SubfieldBase

from south.modelsinspector import add_introspection_rules

from asymmetricbase.logging import logger # @UnusedImport
from asymmetricbase.utils.enum import Enum, EnumItem

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
		if value is None:
			return None
		
		return int(value)
	
	def formfield(self, **kwargs):
		defaults = {
			'min_value' : self.enum.min_value,
			'max_value' : self.enum.max_value
		}
		defaults.update(kwargs)
		return super(EnumField, self).formfield(**defaults)
		

def enum_converter(value):
	if issubclass(value, Enum):
		return 'Migration().gf("{}.{}")'.format(value.__module__, value.__name__)
	
	raise ValueError("Unknown value type `{!r}` for enum argument".format(value))

def default_converter(value):
	if isinstance(value, NOT_PROVIDED) or value is NOT_PROVIDED:
		return None
	
	elif isinstance(value, EnumItem):
		return 'getattr(Migration().gf("{}.{}"), "{}")'.format(value._enum_type_.__module__, value._enum_type_.__name__, value._enum_name_)
	
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
