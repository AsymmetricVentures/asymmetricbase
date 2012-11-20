from asymmetricbase import models
from asymmetricbase.utils.enum import Enum

class TestEnum(Enum):
	VALUE1 = 1
	VALUE2 = 2

class TestModel(models.AsymBaseModel):
	field1 = models.IntegerField()
	field2 = models.CharField(max_length = 255)
	
	class Meta(object):
		app_label = 'tests'


class TestEnumModel(models.AsymBaseModel):
	field1 = models.EnumField(TestEnum)
	
	class Meta(object):
		app_label = 'tests'

class TestEnumModelWithDefault(models.AsymBaseModel):
	field1 = models.EnumField(TestEnum, default = TestEnum.VALUE1)
	
	class Meta(object):
		app_label = 'tests'