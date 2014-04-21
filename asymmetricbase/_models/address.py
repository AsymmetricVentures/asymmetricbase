from __future__ import absolute_import, division, print_function, unicode_literals

from django.db import models

from .base import AsymBaseModel
from asymmetricbase.fields.textfields import LongNameField

class AbstractBaseAddress(AsymBaseModel):
	class Meta(object):
		abstract = True
	
	name = LongNameField(default = "", blank = True) # For easier searching
	
	# Standard contact detail
	address_line_1 = models.CharField("Address", max_length = 255, default = "", blank = True)
	address_line_2 = models.CharField(max_length = 255, default = "", blank = True)
	city = models.CharField(max_length = 30, default = "", blank = True)
	province = models.CharField(max_length = 50, default = "", blank = True)
	postal_code = models.CharField(max_length = 10, default = "", blank = True)
	country = models.CharField(max_length = 25, default = "", blank = True)
	phone = models.CharField(max_length = 25, default = "", blank = True)
	fax = models.CharField(max_length = 25, default = "", blank = True)
	
	
	def __str__(self):
		return "{self.name}, {self.address_line_1}, {self.city}, {self.province}, {self.postal_code}".format(self = self)
	
	@property
	def address_summary(self):
		return u'{self.address_line_1}, {self.city}, {self.postal_code}'.format(self = self)
