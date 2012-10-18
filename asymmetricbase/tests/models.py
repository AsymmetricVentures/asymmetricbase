from django.db import models 
from asymmetricbase.models import AsymBaseModel

class TestModel(AsymBaseModel):
	field1 = models.IntegerField()
	field2 = models.CharField(max_length = 255)
