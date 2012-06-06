from django.utils.log import logger
from django.db.models.signals import post_init

UNSAVED = {}

def track_data(**kwargs):
	"""
	Original implementation: http://justcramer.com/2010/12/06/tracking-changes-to-fields-in-django/
	
	Tracks property changes to a model.
	It can optionally track changes down foreign keys as long as they also are
	decorated with track_data.
	"""
	
	UNSAVED = {}
	
	foreign_keys = kwargs.get('fk', [])
	
	def _store(self):
		"Updates local copy of attributes"
		if self.id:
			self.__track_data = {}
			for field_info in self._meta.fields:
				if hasattr(field_info, 'related') and field_info.related.parent_model == field_info.related.model and field_info.value_from_object(self) == getattr(self, field_info.rel.field_name):
					logger.warning("Not tracking attribute '%s' on %s because it is self-referential." % (field_info.name, repr(self)))
					continue
				self.__track_data[field_info.name] = getattr(self, field_info.name)
				
				try:
					related_class = reduce(getattr, ('field', 'related', 'parent_model'), field_info)
					
					if hasattr(related_class, '__track_data') and field_info.name in foreign_keys:
						changed = getattr(self, field_info.name).whats_changed()
						
						for k, v in changed:
							self.__track_data['{}{}'.format(field_info.name, k)] = v
						
				except AttributeError:
					pass
		else:
			self.__track_data = UNSAVED
	
	def inner(cls):
		
		# local copy of the previous values
		cls.__track_data = {}
		def has_changed(self, field):
			"Returns ``True`` if ``field`` has changed since initialization."
			if self.__track_data is UNSAVED:
				return False
			return self.__track_data.get(field) is not getattr(self, field)
		cls.has_changed = has_changed
		
		def old_value(self, field):
			"Returns the previous value of ``field``"
			return self.__track_data.get(field)
		cls.old_value = old_value
		
		def whats_changed(self):
			"Returns a list of changed attributes."
			changed = {}
			if self.__track_data is UNSAVED:
				return changed
			for k, v in self.__track_data.iteritems():
				if v != getattr(self, k):
					changed[k] = v
			return changed
		cls.whats_changed = whats_changed
		
		# Ensure we are updating local attributes on model init
		def _post_init(sender, instance, **kwargs):
			_store(instance)
		post_init.connect(_post_init, sender = cls, weak = False)
		
		# Ensure we are updating local attributes on model save
		def save(self, *args, **kwargs):
			save._original(self, *args, **kwargs)
			_store(self)
		save._original = cls.save
		cls.save = save
		return cls
	return inner

del UNSAVED
