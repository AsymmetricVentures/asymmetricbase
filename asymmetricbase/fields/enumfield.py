from django.db import models
from django.core import exceptions
from django.db.models.fields import NOT_PROVIDED
from django.db.models.fields.subclassing import SubfieldBase
from django.utils.encoding import smart_unicode
from django.forms import TypedChoiceField

from south.modelsinspector import add_introspection_rules

from asymmetricbase.logging import logger # @UnusedImport
from asymmetricbase.utils.enum import Enum, EnumValue

class EnumField(models.IntegerField):
	__metaclass__ = SubfieldBase
	
	empty_strings_allowed = False
	
	def __init__(self, enum, *args, **kwargs):
		self.enum = enum
		kwargs['choices'] = enum.Choices.items()
		super(EnumField, self).__init__(*args, **kwargs)
	
	def get_default(self):
		if self.has_default():
			default = self.default
			if callable(default):
				default = default()
			if default is None:
				return None
			return default.value
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
	
	def value_to_string(self, obj):
		field_value = self._get_val_from_obj(obj)
		
		if field_value is not None:
			field_value = field_value.value
		
		return smart_unicode(field_value)
	
	def validate(self, value, model_instance):
		return value in self.enum
	
	def get_prep_value(self, value):
		if value is None:
			return None
		
		return int(value)
	
	def formfield(self, **kwargs):
		defaults = {
			'required': not self.blank,
			'label': self.verbose_name,
			'help_text': self.help_text,
			'choices': self.get_choices(include_blank = self.blank),
			'coerce': self.to_python,
			'empty_value': None,
		}
		
		if self.has_default():
			if callable(self.default):
				defaults['initial'] = self.default
				defaults['show_hidden_initial'] = True
			else:
				defaults['initial'] = self.get_default()
		
		defaults.update(kwargs)
		
		return EnumFormField(**defaults)

class EnumFormField(TypedChoiceField):
	def prepare_value(self, value):
		if isinstance(value, EnumValue):
			return smart_unicode(value.value)
		return value

def enum_converter(value):
	if issubclass(value, Enum):
		return 'Migration().gf("{}.{}")'.format(value.__module__, value.__name__)
	
	raise ValueError("Unknown value type `{!r}` for enum argument".format(value))

def default_converter(value):
	if isinstance(value, NOT_PROVIDED) or value is NOT_PROVIDED:
		return None
	elif isinstance(value, EnumValue):
		#return 'getattr(Migration().gf("{}.{}"), "{}")'.format(value._enum_type_.__module__, value._enum_type_.__name__, value._enum_name_)
		return repr(value.value)
	elif value is None:
		return repr(None)
	
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
