import base64
import uuid
import time
import datetime
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto import exception as boto_exceptions
from django.utils.timezone import utc
from django.db import models
from django.db.utils import DatabaseError
from django.core.exceptions import ValidationError
from django.conf import settings
from django_extensions.db.fields.json import JSONField

class S3File(models.Model):
	file_name = models.CharField(max_length = 256)
	metadata = JSONField(max_length = 4096)
	_s3_key = models.CharField(max_length = 256)
	_s3_version_id = models.CharField(max_length = 256)
	
	@property
	def file_data(self):
		if not getattr(self, '_file_data', None):
			self._file_data = self._load_from_s3()
		return self._file_data
	
	@file_data.setter
	def file_data(self, value):
		self._file_data = value
	
	def list_versions(self):
		"Returns a list of all versions of this file"
		if not self._s3_key:
			return [] # we don't have a key yet
		bucket = self._get_s3_bucket(
			bucket_name = self._get_bucket_name(),
			assert_versioning_enabled = True
		)
		return bucket.list_versions(prefix = self._s3_key)
	
	class Meta:
		abstract = True
	
	def get_file_prefix(self):
		# Subclasses can use to append a prefix to file name
		return 'asymm'
	
	def get_file_postfix(self):
		now = datetime.datetime.utcnow().replace(tzinfo=utc)
		return now.strftime("-%Y.%m.%d.%H.%M.%S")
	
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
		return  base64.b64decode(encoded_value)
	
	def _put_object_in_s3(self, bucket_name, object_name, value):
		key = self._get_s3_key(bucket_name, object_name, assert_versioning_enabled = True)
		encoded_value = base64.b64encode(value)
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
		if d.has_key('Versioning') and d['Versioning'] == 'Enabled':
			# already has versioning enabled
			return
		bucket.configure_versioning(versioning = True)
		# need to wait until AWS syncs s3. this is fine,
		# since we only do this once every few months (when bucket properties change)
		time.sleep(15)
	
	@classmethod
	def _get_s3_connection(cls):
		aws_access_key_id = (settings, "AWS_S3_FILES_ACCESS_KEY_ID", None)
		aws_secret_access_key = (settings, "AWS_S3_FILES_SECRET_ACCESS_KEY", None)
		assert aws_access_key_id and aws_secret_access_key, \
			"Please assign values for AWS_S3_FILES_ACCESS_KEY_ID and AWS_S3_FILES_SECRET_ACCESS_KEY in settings"
		try:
			# TODO: We may want to move to a connection pool
			return S3Connection(aws_access_key_id, settings.aws_secret_access_key)
		except boto_exceptions.BotoClientError as e:
			raise DatabaseError("Unable to connect to S3.\nBoto Exception:\n{}".format(e))
	
	@classmethod
	def _get_bucket_name(cls):
		test_bucket = getattr(settings, "AWS_S3_FILES_BUCKET_TEST", None)
		real_bucket = getattr(settings, "AWS_S3_FILES_BUCKET", None)
		assert test_bucket and real_bucket,\
		"Please assign values for AWS_S3_FILES_BUCKET_TEST and AWS_S3_FILES_BUCKET in settings"
		try:
			in_test = settings.IS_IN_TEST == True
		except AttributeError:
			in_test = False
		if in_test:
			return test_bucket
		else:
			return real_bucket
