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

import unittest
import StringIO
import os
import random

from asymmetricbase.tests.models import TestS3FileModel, TestS3FileWithPreviewModel
from asymmetricbase.testing.base_with_models import BaseTestCaseWithModels

try:
	import Image
except ImportError:
	Image = None

class TestS3File(BaseTestCaseWithModels):
	def test_simple_load_save(self):
		f1 = TestS3FileModel(file_data = b"SOME FILE CONTENT")
		f2 = TestS3FileModel(file_data = b"SOME OTHER FILE CONTENT")
		f3 = TestS3FileModel(file_data = b"AND YET ANOTHER FILE CONTENT")
		f1.metadata = {'some_field': 'some value', 'another_field': 12345}
		f1.save()
		f2.save()
		f3.save()
		f1_loaded = TestS3FileModel.objects.get(id = f1.id)
		f2_loaded = TestS3FileModel.objects.get(id = f2.id)
		f3_loaded = TestS3FileModel.objects.get(id = f3.id)
		self.assertEquals(f1_loaded.file_data, b"SOME FILE CONTENT")
		self.assertEquals(f2_loaded.file_data, b"SOME OTHER FILE CONTENT")
		self.assertEquals(f3_loaded.file_data, b"AND YET ANOTHER FILE CONTENT")
		self.assertEquals(f1_loaded.metadata, {'some_field': 'some value', 'another_field': 12345})
	
	def test_save_load_large_random_sized_blocks(self):
		random_blocks = []
		for i in range(10):
			random_blocks.append(self._generate_random_block())
		
		d_ids = []
		for i in range(10):
			d = TestS3FileModel(file_data = random_blocks[i])
			d.save()
			d_ids.append(d.id)
		self.assertEquals(len(d_ids), 10)
		
		for i in range(10):
			d_id = d_ids[i]
			d_loaded = TestS3FileModel.objects.get(id = d_id)
			self.assertEquals(d_loaded.file_data, random_blocks[i])
	
	def _generate_random_block(self):
		block_length = random.randrange(1000, 2000)
		return b"".join(chr(random.randrange(0, 256)) for _i in xrange(block_length))

@unittest.skipUnless(Image, "Image Preview is only enabled if PIL or Pillow is installed")
class TestS3FileWithPreview(BaseTestCaseWithModels):
	def test_simple_load_save(self):
		test_image_file = os.path.join(os.path.dirname(__file__), "tiger.jpg")
		with open(test_image_file) as fp:
			f = TestS3FileWithPreviewModel(
				file_data = fp.read(),
				file_name = "tiger.jpg"
			)
		f.save()
		f.save_preview_image()
		f_loaded = TestS3FileWithPreviewModel.objects.get(id = f.id)
		preview_data = f_loaded.get_preview_image_data()
		preview_file = StringIO.StringIO(preview_data)
		image_preview = Image.open(preview_file)
		width, height = image_preview.size
		self.assertGreater(width, 0)
		self.assertGreater(height, 0)
		self.assertLessEqual(width, TestS3FileWithPreviewModel.Constants.PREVIEW_IMAGE_WIDTH)
		self.assertLessEqual(height, TestS3FileWithPreviewModel.Constants.PREVIEW_IMAGE_HEIGHT)


