from collections import OrderedDict
import uuid

from django.db import models
from django.utils import timezone
from django.dispatch.dispatcher import receiver
from django.db.models import signals
from django.db.utils import IntegrityError

from asymmetricbase.logging import audit_logger

class AsymBaseModel(models.Model):
	uuid = models.CharField(max_length = 40, blank = True)
	date_created = models.DateTimeField(auto_now_add = True, default = timezone.now)
	date_updated = models.DateTimeField(auto_now = True, default = timezone.now)
	
	class Meta(object):
		abstract = True
	
	def _audit_log(self, access_type, success):
		msg = 'Model Access'
		audit_logger.info(msg, extra = {
			'log_type' : LogEntryType.MODEL,
			'model' : self,
			'access_type' : access_type,
			'success' : success
		})
	
	def _object_saved_before(self):
		''' Returns True if this object has been saved before '''
		return hasattr(self, 'id') and self.id is not None

@receiver(signal = signals.pre_save, dispatch_uid = 'create_model_uuid')
def asym_model_base_presave(sender, instance, raw, using, **kwargs):
	if not isinstance(instance, AsymBaseModel):
		return
	
	if not instance.uuid:
		instance.uuid = _generate_unique_uuid(instance)
		
@receiver(signal = signals.post_save, dispatch_uid = 'write_audit_log')
def asym_model_base_postsave(sender, instance, created, raw, using, **kwargs):
	if not isinstance(instance, AsymBaseModel):
		return
	
	if created:
		instance._audit_log(access_type = AccessType.ADD, success = True)
	else:
		instance._audit_log(access_type = AccessType.WRITE, success = True)

@receiver(signal = signals.post_init, dispatch_uid = 'read_permission_check')
def asym_model_base_postinit(sender, instance, **kwargs):
	if not isinstance(instance, AsymBaseModel):
		return
	
	if not instance._object_saved_before():
		return # this is a constructor call. CanAdd will be checked it in pre_save
	
	instance._audit_log(access_type = AccessType.READ, success = True)

def _generate_unique_uuid(instance):
	kls = instance.__class__
	for dummy in range(100):
		new_uuid = uuid.uuid4().hex[0:10]
		if not kls.objects.filter(uuid = new_uuid).exists():
			return new_uuid
	raise IntegrityError('Unable to generate a unique uuid for model: {}'.format(kls))


class LogEntryType(object):
	MODEL = 'model'
	VIEW = 'view'
	LOGIN = 'login'
	ASSIGN = 'assign'
	OTHER = 'other'
	
	Choices = OrderedDict([
		(MODEL, 'Model'),
		(VIEW, 'View'),
		(LOGIN, 'Login'),
		(ASSIGN, 'Assign'),
		(OTHER, 'OTHER')
	])

class AccessType(object):
	READ = 'read'
	WRITE = 'write'
	ADD = 'add'
	GRANT = 'grant'
	ASSIGN = 'assign'
	UNASSIGN = 'unassign'
	VIEW = 'view'
	OTHER = 'other'
	
	Choices = OrderedDict([
		(READ, 'Read'),
		(WRITE, 'Write'),
		(ADD, 'Add'),
		(GRANT, 'Grant'),
		(ASSIGN, 'assign'),
		(UNASSIGN, 'unassign'),
		(VIEW, 'View'),
		(OTHER, 'OTHER')
	])


class ObjectContent(models.Model):
	time_stamp = models.DateTimeField('action time', auto_now = True, default = timezone.now)
	content_in_json = models.TextField('Object Content in JSON format')
	
	
	def __unicode__(self):
		return u'content_in_json: {self.content_in_json} '.format(self = self)
	
	def get_original_object(self):
		from django.core import serializers
		obj = list(serializers.deserialize("json", self.content_in_json))[0].object
		return obj

class AuditEntry(models.Model):
	log_type = models.CharField(max_length = 10, choices = LogEntryType.Choices.items())
	access_type = models.CharField(max_length = 10, choices = AccessType.Choices.items())
	time_stamp = models.DateTimeField('Time Stamp', auto_now = True, default = timezone.now)
	user_id = models.IntegerField('UserBase.ID', null = True, blank = True)
	ip = models.IPAddressField("Origin IP")	
	message = models.TextField('change message', blank = True)
	model_name = models.CharField('for LogEntryType == MODEL', max_length = 256, null = True, blank = True)
	view_name = models.CharField('for LogEntryType == VIEW', max_length = 256, null = True, blank = True)
	success = models.NullBooleanField(null = True)
	object_content = models.ForeignKey(ObjectContent, null = True)
	
	class Meta(object):
		ordering = ('time_stamp',)
	
	def __unicode__(self):
		return u"""Time: {time_stamp}
IP: {ip}
User-ID: {user_id}
Log Type: {log_type}
Access Type: {access_type}
Model Name: {model_name}
View Name: {view_name}
Success: {success}
Message: {message}
Object Content: {object_content}""".format(
			time_stamp = self.time_stamp,
			ip = self.ip,
			user_id = self.user_id,
			log_type = LogEntryType.Choices[self.log_type],
			access_type = AccessType.Choices[self.access_type],
			model_name = self.model_name,
			view_name = self.view_name,
			success = self.success,
			message = self.message,
			object_content = self.object_content
		)

class LogEntry(models.Model):
	date_created = models.DateTimeField(default = timezone.now)
	level = models.IntegerField()
	pathname = models.CharField(max_length = 255)
	lineno = models.IntegerField()
	msg = models.TextField(blank = True)
	args = models.TextField(blank = True)
	exc_info = models.TextField(blank = True)
	func = models.TextField(blank = True)
