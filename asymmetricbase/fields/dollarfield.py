from decimal import Decimal

from django.db import models

from south.modelsinspector import add_introspection_rules

from asymmetricbase.logging import logger # @UnusedImport

ZERO_DOLLARS = Decimal('0.00')

class DollarField(models.DecimalField):
	
	def __init__(self, *args, **kwargs):
		kwargs.setdefault('default', ZERO_DOLLARS)
		kwargs.setdefault('max_digits', 15)
		kwargs.setdefault('decimal_places', 2)
		
		super(DollarField, self).__init__(*args, **kwargs)

add_introspection_rules([], ['^asymmetricbase\.fields\.dollarfield\.DollarField'])
