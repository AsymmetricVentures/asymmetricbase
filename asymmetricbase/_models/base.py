# from collections import OrderedDict

from django.db import models
from django.utils import timezone
from django.dispatch.dispatcher import receiver
from django.db.models import signals
from django.forms.models import model_to_dict

from asymmetricbase.logging import audit_logger
from asymmetricbase._models.logger_models import LogEntryType, AccessType
from asymmetricbase.fields import UUIDField

class AsymBaseModel(models.Model):
	# The next two lines for for eclipse so that it stops reporting _meta as unknown
	_meta = models.options.Options
	del _meta
	
	
	uuid = UUIDField()
	date_created = models.DateTimeField(auto_now_add = True, default = timezone.now)
	date_updated = models.DateTimeField(auto_now = True, default = timezone.now)
	
	class Meta(object):
		abstract = True
		app_label = 'shared'
	
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
	
	def __json__(self, encoder):
		return model_to_dict(self, exclude = ['id'])

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
		return  # this is a constructor call. CanAdd will be checked it in pre_save
	
	instance._audit_log(access_type = AccessType.READ, success = True)
