#from collections import OrderedDict

from asymmetricbase import models
from asymmetricbase.utils.enum import Enum

class TestEnum(Enum):
	VALUE1 = 1
	VALUE2 = 2
	
#class TestOldEnum(object):
#	VALUEA = 1
#	VALUEB = 2
#	VALUEC = 3
#	
#	Choices = OrderedDict([
#		(VALUEA, 'A'),
#		(VALUEB, 'B'),
#		(VALUEC, 'C'),
#	])

class TestModel(models.AsymBaseModel):
	field1 = models.IntegerField()
	field2 = models.CharField(max_length = 255)
	
	class Meta(object):
		app_label = 'tests'

class FKTestModel(models.AsymBaseModel):
	test_model = models.ForeignKey(TestModel)
	field1 = models.IntegerField()
	field2 = models.CharField(max_length = 255)
	
	class Meta(object):
		app_label = 'tests'

class FKFKTestModel(models.AsymBaseModel):
	fk_test_model = models.ForeignKey(FKTestModel)
	field1 = models.IntegerField()
	field2 = models.CharField(max_length = 255)
	
	class Meta(object):
		app_label = 'tests'

class TestEnumModel(models.AsymBaseModel):
	field1 = models.EnumField(TestEnum)
	
	class Meta(object):
		app_label = 'tests'

class TestEnumModel1(models.AsymBaseModel):
	field1 = models.EnumField(TestEnum)
	field2 = models.EnumField(TestEnum)
	field3 = models.EnumField(TestEnum)
	
	class Meta(object):
		app_label = 'tests'


class TestEnumModelWithDefault(models.AsymBaseModel):
	field1 = models.EnumField(TestEnum, default = TestEnum.VALUE1)
	
	class Meta(object):
		app_label = 'tests'

#class TestOldEnumModel(models.AsymBaseModel):
#	field1 = models.PositiveSmallIntegerField(choices = TestOldEnum.Choices.items())
#	
#	class Meta(object):
#		app_label = 'tests'
#
#class TestOldEnumModelWithDefault(models.AsymBaseModel):
#	field1 = models.PositiveSmallIntegerField(choices = TestOldEnum.Choices.items(), default = TestOldEnum.VALUEC)
#	
#	class Meta(object):
#		app_label = 'tests'
