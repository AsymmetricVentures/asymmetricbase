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

import base64
import mimetypes
import uuid
import time
import threading

try:
	from urllib.parse import quote as url_quote
except ImportError:
	from urllib import quote as url_quote

try:
	from io import BytesIO as ImageBufferIO
except ImportError:
	import StringIO.StringIO as ImageBufferIO

from django.utils import timezone
from django.db import models
from django.db.utils import DatabaseError
from django.core.exceptions import ValidationError
from django.conf import settings

from django_extensions.db.fields.json import JSONField

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto import exception as boto_exceptions

from asymmetricbase.logging import logger

from .base import AsymBaseModel

try:
	import Image # Try to import PIL
except ImportError:
	try:
		from PIL import Image # try to import Pillow
	except ImportError:
		Image = None	# PIL/Pillow not installed. File Preview is disabled

thread_safe_connection_cache = threading.local()

class S3File(AsymBaseModel):
	"""
	This class should always deal with binary data
	"""
	file_name = models.CharField(max_length = 256)
	# TODO: check if this works in all cases, 
	#       I had to do some hacky things in our other classes to get JSONField to work
	metadata = JSONField(max_length = 4096)
	
	_s3_key = models.CharField(max_length = 256)
	_s3_version_id = models.CharField(max_length = 256)
	
	class Meta(object):
		abstract = True
	
	@property
	def file_data(self):
		if not getattr(self, '_file_data', None):
			self._file_data = self._load_from_s3()
		
		return self._file_data
	
	@file_data.setter
	def file_data(self, value):
		self._file_data = value
	
	@property
	def content_type(self):
		if not self.file_name:
			return None
		
		content_type, _ = mimetypes.guess_type(self.file_name)
		return content_type
	
	def list_versions(self):
		"Returns a list of all versions of this file"
		if not self._s3_key:
			return [] # we don't have a key yet
		
		bucket = self._get_s3_bucket(
			bucket_name = self._get_bucket_name(),
			assert_versioning_enabled = True
		)
		return bucket.list_versions(prefix = self._s3_key)
	
	def get_file_prefix(self):
		# Subclasses can use to append a prefix to file name
		return 'asymm'
	
	def get_file_postfix(self):
		return timezone.now().strftime("-%Y.%m.%d.%H.%M.%S")
	
	def save(self, *args, **kwargs):
		_file_data = getattr(self, '_file_data', None)
		if not self._s3_key:
			if not _file_data:
				raise ValidationError("S3File.file_data may not be None")
			self._s3_key = self._generate_s3_key()
		
		if _file_data:
			bucket_name = self._get_bucket_name()
			self._put_object_in_s3(bucket_name, self._s3_key, _file_data)
		
		super(S3File, self).save(*args, **kwargs)
	
	# private
	def _load_from_s3(self):
		if not self._s3_key:
			return None
		bucket_name = self._get_bucket_name()
		return self._get_object_from_s3(bucket_name, self._s3_key)
	
	# private
	def _generate_s3_key(self):
		return '{}/{}{}'.format(self.get_file_prefix(), uuid.uuid4(), self.get_file_postfix())
	
	def _get_object_from_s3(self, bucket_name, object_name):
		key = self._get_s3_key(bucket_name, object_name)
		encoded_value = key.get_contents_as_string()
		return bytes(base64.b64decode(encoded_value))
	
	def _put_object_in_s3(self, bucket_name, object_name, value):
		key = self._get_s3_key(bucket_name, object_name, assert_versioning_enabled = True)
		encoded_value = base64.b64encode(bytes(value))
		key.set_contents_from_string(encoded_value, encrypt_key = True)
		self._s3_version_id = key.version_id
	
	def _get_s3_key(self, bucket_name, object_name, assert_versioning_enabled = False):
		bucket = self._get_s3_bucket(bucket_name, assert_versioning_enabled)
		try:
			return Key(bucket = bucket, name = object_name)
		except boto_exceptions.BotoClientError as e:
			raise DatabaseError(
				"Error retrieving object from S3.\n Bucket: {}\n Object Name: {}\n Boto Exception:\n {}".format(
					bucket_name, object_name, e
				)
			)
	
	@classmethod
	def _get_s3_bucket(cls, bucket_name, assert_versioning_enabled):
		try:
			connection = cls._get_s3_connection()
			if not connection.lookup(bucket_name):
				connection.create_bucket(bucket_name)
			
			bucket = connection.get_bucket(bucket_name)
			
			if assert_versioning_enabled:
				cls._assert_bucket_has_versioning_enabled(bucket)
				
			return bucket
		except boto_exceptions.S3ResponseError as e:
			raise DatabaseError(
				"Error retrieving bucket from S3.\nBucket: {}\nBoto Exception:\n{}".format(
					bucket_name, e
				)
			)
	
	@classmethod
	def _assert_bucket_has_versioning_enabled(cls, bucket):
		d = bucket.get_versioning_status()
		if 'Versioning' in d and d['Versioning'] == 'Enabled':
			# already has versioning enabled
			return
		bucket.configure_versioning(versioning = True)
		# need to wait until AWS syncs s3. this is fine,
		# since we only do this once every few months (when bucket properties change)
		time.sleep(15)
	
	@classmethod
	def _get_s3_connection(cls):
		s3_connection = getattr(thread_safe_connection_cache, 's3_connection', None)
		
		if s3_connection:
			return s3_connection
		
		aws_access_key_id = getattr(settings, 'AWS_S3_FILES_ACCESS_KEY_ID', None)
		aws_secret_access_key = getattr(settings, 'AWS_S3_FILES_SECRET_ACCESS_KEY', None)
		assert aws_access_key_id and aws_secret_access_key, \
			"Please assign values for AWS_S3_FILES_ACCESS_KEY_ID and AWS_S3_FILES_SECRET_ACCESS_KEY in settings"
		
		try:
			connection = S3Connection(aws_access_key_id, aws_secret_access_key) # TODO: We may want to move to a connection pool
			setattr(thread_safe_connection_cache, 's3_connection', connection)
		except boto_exceptions.BotoClientError as e:
			raise DatabaseError("Unable to connect to S3.\nBoto Exception:\n{}".format(e))
		
		return thread_safe_connection_cache.s3_connection
	
	@classmethod
	def _get_bucket_name(cls):
		test_bucket = getattr(settings, 'AWS_S3_FILES_BUCKET_TEST', None)
		real_bucket = getattr(settings, 'AWS_S3_FILES_BUCKET', None)
		assert test_bucket and real_bucket, \
		"Please assign values for AWS_S3_FILES_BUCKET_TEST and AWS_S3_FILES_BUCKET in settings"
		
		try:
			in_test = settings.IS_IN_TEST == True
		except AttributeError:
			in_test = False
		
		return real_bucket if not in_test else test_bucket

class S3FileWithPreview(S3File):
	class Meta(object):
		abstract = True
	
	class Constants(object):	# Override in subclass
		PREVIEW_IMAGE_WIDTH = None
		PREVIEW_IMAGE_HEIGHT = None
	
	def get_preview_image_data(self):
		bucket_name = self._get_bucket_name()
		try:
			return self._get_object_from_s3(bucket_name, self._generate_preview_key())
		except IOError:
			return b""
	
	def get_preview_type(self):
		return 'image/jpeg'	# only jpeg previews are currently supported
	
	def save_preview_image(self):
		assert Image, "PIL or Pillow is required for image preview"
		assert self.is_image(), "Cannot save preview image for non-image file"
		assert self.id and self._s3_key, "Can only save image preview once the image is saved"
		assert self.Constants.PREVIEW_IMAGE_HEIGHT and self.Constants.PREVIEW_IMAGE_WIDTH, "Set preview image dimensions in the subclass"
		
		image_file = ImageBufferIO(self.file_data)
		output = ImageBufferIO()
		
		self._generate_thumbnail(image_file, output)
		
		preview_image_data = output.getvalue()
		preview_image_s3_key = self._generate_preview_key()
		bucket_name = self._get_bucket_name()
		
		self._put_object_in_s3(bucket_name, preview_image_s3_key, preview_image_data)
	
	def _generate_thumbnail(self, image_file, output, size = None):
		try:
			if Image.isImageType(image_file):
				image = image_file
			else:
				image = Image.open(image_file)
			if image.mode != 'RGB':
				image = image.convert('RGB')
			if size is None:
				size = [self.Constants.PREVIEW_IMAGE_WIDTH, self.Constants.PREVIEW_IMAGE_HEIGHT]
			image.thumbnail(
				size,
				Image.ANTIALIAS
			)
			image.save(output, 'JPEG')
		except IOError:
			logger.exception('Could not generate thumbnail')
			raise PreviewImageGenerationFailed()

	def is_image(self):
		return self.content_type in ['image/png', 'image/jpeg', 'image/gif']

	def _generate_preview_key(self):
		return "{}-preview".format(self._s3_key)
	
	def get_data_url(self, max_width = None):
		data_url = b'data:{};base64,{}'
		
		if self.is_image():
			image_file = ImageBufferIO(self.file_data)
			output = ImageBufferIO()
			
			try:
				image = Image.open(image_file)
				
				s = image.size
				
				if max_width and s[0] > max_width:
					ratio = max_width / s[0]
					width = s[0] * ratio
					height = s[1] * ratio
					self._generate_thumbnail(image, output, (width, height))
					
					file_data = output.getvalue()
				else:
					file_data = image_file.getvalue()
			except IOError:
				file_data = self.file_data
				logger.exception('Error when trying to resize image for data: url')
		else:
			file_data = self.file_data
			
		data = bytes(url_quote(file_data.encode('base64')))
		
		return data_url.format(self.content_type, data)

class PreviewImageGenerationFailed(Exception):
	pass
