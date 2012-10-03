from base import Display

class SimpleTableDisplay(Display):
	class Meta(object):
		template_name = ('asymmetricbase/displaymanager/fields.djhtml', 'asymmetricbase/displaymanager/base.djhtml')
	
	@property
	def columns(self):
		return self._meta.fields
	
	@property
	def items(self):
		return self.obj
	
	
