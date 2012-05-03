from django.forms import forms
from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode
from django.dispatch import Signal

from asymmetricbase.jinja import jinja_env

boundfield_props = Signal() 

class BoundField(forms.BoundField):
	template_module = jinja_env.get_template('asymmetricbase/boundfield/default.djhtml').module
	
	def _get_fields(self):
		if self.is_hidden:
			return self
		
		if self.label:
			label = conditional_escape(force_unicode(self.label))
			
			label_css = ('required',) if self.field.required else ('',)
			label_css = self.css_classes(label_css)
			
			label = self.label_tag(label, attrs = {'class' : label_css}) or ''
		else:
			label = ''
		
		if self.field.help_text:
			help_text = self.template_module.help_text(self.field.help_text)
		else:
			help_text = u''
		
		if self.field.required:
			required_text = self.template_module.required_text()
		else:
			required_text = u''
		
		return dict(
			label = label,
			required = required_text,
			field = self,
			help_text = help_text,
		)
	
	def _render_with_template(self, name):
		return getattr(self.template_module, name)(**self._get_fields())
	
	def _render_from_module(self, template_module_call):
		return template_module_call(**self._get_fields())
	
	vseg = property(lambda self: self._render_with_template('vblock_segment'))
	hseg = property(lambda self: self._render_with_template('hblock_segment'))
	rhseg = property(lambda self: self._render_with_template('rhblock_segment'))

# Give other parts of the code a chance to register custom functions on boundfield
boundfield_props.send(sender = BoundField)

setattr(forms, 'BoundField', BoundField)
