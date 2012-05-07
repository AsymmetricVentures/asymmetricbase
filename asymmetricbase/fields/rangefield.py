from django.db.models import IntegerField

from south.modelsinspector import add_introspection_rules

from asymmetricbase.logging import logger #@UnusedImport

class IntegerRangeField(IntegerField):
	def __init__(self, *args, **kwargs):
		self.min_value = kwargs.pop('min_value', 0)
		self.max_value = kwargs.pop('max_value', None)
		
		super(IntegerRangeField, self).__init__(*args, **kwargs)
		
	def formfield(self, **kwargs):
		defaults = {
			'min_value': self.min_value,
			'max_value': self.max_value, }
		defaults.update(kwargs)
		return super(IntegerRangeField, self).formfield(**defaults)


add_introspection_rules([], ['^asymmetricbase\.fields\.rangefield\.IntegerRangeField'])
