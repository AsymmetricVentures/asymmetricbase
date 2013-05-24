from __future__ import absolute_import, division, print_function, unicode_literals

from asymmetricbase import models
from asymmetricbase.logging import logger # @UnusedImport

class AbstractBaseAddress(models.AsymBaseModel):
	class Meta(object):
		abstract = True
	
	name = models.LongNameField() # For easier searching
	
	# Standard contact detail
	address_line_1 = models.CharField("Address", max_length = 255, default = "")
	address_line_2 = models.CharField(max_length = 255, default = "")
	city = models.CharField(max_length = 30, default = "")
	province = models.CharField(max_length = 50, default = "")
	postal_code = models.CharField(max_length = 10, default = "")
	phone = models.CharField(max_length = 25, default = "")
	fax = models.CharField(max_length = 25, default = "")
	
	
	def __str__(self):
		return "{self.name}, {self.address_line_1}, {self.city}, {self.province}, {self.postal_code}".format(self = self)
	
	@property
	def address_summary(self):
		return u'{self.address_line_1}, {self.city}, {self.postal_code}'.format(self = self)
	

class Address(AbstractBaseAddress):
	class Meta(object):
		app_label = 'shared'
