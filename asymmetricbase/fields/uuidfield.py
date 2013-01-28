import uuid

from django.db import models
from django.db.utils import IntegrityError

from south.modelsinspector import add_introspection_rules

from asymmetricbase.logging import logger # @UnusedImport

class UUIDField(models.CharField):
	
	def __init__(self, *args, **kwargs):
		kwargs['max_length'] = 40
		kwargs['blank'] = True
		self.auto_add = kwargs.pop('auto_add', True)
		
		super(UUIDField, self).__init__(*args, **kwargs)
	
	def pre_save(self, model_instance, add):
		if (self.auto_add and add):
			kls = model_instance.__class__
			for _ in range(100):
				new_uuid = uuid.uuid4().hex[0:10]
				if not kls.objects.filter(uuid = new_uuid).exists():
					setattr(model_instance, self.attname, new_uuid)
					return new_uuid
			raise IntegrityError('Unable to generate a unique uuid for model: {}'.format(kls))
		
		else:
			return super(UUIDField, self).pre_save(model_instance, add)

add_introspection_rules([], ['^asymmetricbase\.fields\.uuidfield\.UUIDField'])
