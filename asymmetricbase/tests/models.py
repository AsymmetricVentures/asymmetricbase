# -*- coding: utf-8 -*-
#    Asymmetric Base Framework - A collection of utilities for django frameworks
#    Copyright (C) 2013  Asymmetric Ventures Inc.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; version 2 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from __future__ import absolute_import, division, print_function, unicode_literals

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

class TestS3FileModel(models.S3File):
	pass

class TestS3FileWithPreviewModel(models.S3FileWithPreview):
	class Constants(object):
		PREVIEW_IMAGE_WIDTH = 50
		PREVIEW_IMAGE_HEIGHT = 50
