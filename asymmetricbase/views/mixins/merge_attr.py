from collections import OrderedDict

from django.dispatch import Signal

from asymmetricbase.logging import logger #@UnusedImport

pre_merge = Signal(providing_args = ['instance', 'attr'])
post_merge = Signal(providing_args = ['instance', 'attr', 'merged'])

class MergeAttrMixin(object):
	@classmethod
	def _merge_attr(cls, attrname, process = None):
		attr_ret = OrderedDict()
		
		for base_class in cls.__bases__:
			if issubclass(base_class, MergeAttrMixin):
				attr_ret.update(base_class._merge_attr(attrname, process))
		
		if not hasattr(cls, attrname):
			return attr_ret
		
		new_attr = getattr(cls, attrname)
		
		if isinstance(new_attr, (list, tuple)):
			for item in new_attr:
				if item not in attr_ret:
					if process is not None:
						item = process(item)
						
					attr_ret[item] = True
					
		elif isinstance(new_attr, dict):
			for key, value in new_attr.items():
				if process is not None:
					value = process(value)
				
				attr_ret[key] = value
		
		return attr_ret
	
	def _merge_attr_signal(self, attrname, process = None):
		pre_merge.send(sender = self, instance = self, attr = attrname)
		ret = self._merge_attr(attrname, process)
		post_merge.send(sender = self, instance = self, attr = attrname, merged = ret)
		return ret
