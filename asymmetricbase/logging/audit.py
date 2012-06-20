import logging

from django.conf import settings
from asymmetricbase.models import AuditEntry, AccessType, LogEntryType, \
	ObjectContent

class AuditLoggingHandler(logging.Handler):
	"""
		Performs our Audit logging. If there is a model included in the record,
		we will also include Object Retention info
	"""
	
	def _get_current_user_info(self):
		pass
	
	def emit(self, record):
		log_generator = AuditLogGenerator(record)
		log_generator.generate()

class AuditLogGenerator(object):
	def __init__(self, record):
		self.record = record
	
	def generate(self):
		self._get_access_type()
		self._get_log_type()
		self._get_success()
		if self._do_ignore_log():
			return
		self._get_current_user_info()
		self._get_ip()
		self._get_model()
		self._get_view_name()
		self._save_object_contnt()
		self._save_log_entry()
	
	def _save_log_entry(self):
		from django.db import transaction
		with transaction.commit_on_success():
			l = AuditEntry(
				log_type = self.log_type,
				access_type = self.access_type,
				user_id = self.user.id if self.user is not None else None,
				ip = self.ip,
				message = self.record.msg,
				model_name = self.model_str,
				view_name = self.view_name,
				success = self.success,
				object_content = self.object_content,
			)
			l.save()
	
	def _save_object_contnt(self):
		if not self._is_save_object_content_required():
			self.object_content = None
			return
		
		from django.core import serializers
		
		# serializer only accepts iterables!
		content_in_json = serializers.serialize('json', [self.model], ensure_ascii = False)
		oc = ObjectContent(content_in_json = content_in_json)
		oc.save()
		
		self.object_content = oc
	
	def _is_save_object_content_required(self):
		if self.log_type != LogEntryType.MODEL:
			return False
		if self.access_type not in (AccessType.ADD, AccessType.WRITE):
			return False
		if not self.success:
			return False
		return True
	
	def _get_current_user_info(self):
#		from project.shared import thread_globals
#		try:
#			self.user = thread_globals.request.user
#		except AttributeError:
#			self.user = None
		pass
	
	def _get_ip(self):
		#from project.shared import thread_globals
		#self.ip = thread_globals.request.META['REMOTE_ADDR']
		pass
	
	def _get_access_type(self):
		try:
			self.access_type = self.record.access_type
		except AttributeError:
			self.access_type = AccessType.OTHER
	
	def _get_log_type(self):
		try:
			self.log_type = self.record.log_type
		except AttributeError:
			self.log_type = LogEntryType.OTHER
	
	def _get_model(self):
		try:
			self.model = self.record.model
			self.model_str = "{model.__class__.__name__}.{model.id}".format(model = self.model)
		except AttributeError:
			self.model = None
			self.model_str = None
	
	def _get_view_name(self):
		try:
			self.view_name = self.record.view_name
		except AttributeError:
			self.view_name = None
	
	def _get_success(self):
		try:
			self.success = self.record.success
		except AttributeError:
			self.success = None
	
	def _do_ignore_log(self):
		if (not settings.LOG_MODEL_ACCESS_READ) and \
			self.log_type == LogEntryType.MODEL and \
			self.access_type == AccessType.READ and \
			self.success == True:
			return True
		return False
