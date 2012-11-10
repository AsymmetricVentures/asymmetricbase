from django.forms import * # @UnusedWildImport pylint: disable-msg=W0401
from django import forms # @Reimport
from django.forms.models import modelformset_factory, BaseModelFormSet
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.conf import settings

import jinja2

from asymmetricbase.forms.boundfield import BoundField
from asymmetricbase.jinja import jinja_env

HTML5 = getattr(settings, 'ASYM_HTML5', False)
HTML5_WIDGETS = getattr(settings, 'ASYM_HTML5_WIDGETS', {})

if HTML5:
	from asymmetricbase.forms.html5_widgets import * # pylint: disable-msg=W0401

# from https://gist.github.com/972162/3230682034aefe517e0c08b4ff38a6c37509a0e9
def monkey_patch_django():
	"""
	Patching some django objects to make them "safe" for jinja's escape() function.
	Good for us it uses __html__() method.
	"""
	# Django's SafeString and SafeUnicode should not be escaped:
	from django.utils.safestring import SafeData
	SafeData.__html__ = lambda self: self
	
	from django.forms.formsets import BaseFormSet
	from django.forms.util import ErrorDict, ErrorList
	
	# If unicode returns SafeData, then escape will pass it outside unmodified thanks to patch above
	# If it's just a string it will be escaped
	for cls in (BaseForm, Media, BoundField, BaseFormSet, ErrorDict, ErrorList):
		cls.__html__ = lambda self: jinja2.escape(unicode(self))
	
class BaseFormMixin(object):
	
	required_css_class = 'field_required'
	error_css_class = 'field_error'
	
	def __init__(self, *args, **kwargs):
		super(BaseFormMixin, self).__init__(*args, **kwargs)
		
		if not hasattr(self, 'Meta'):
			return
		
		validate = getattr(self.Meta, 'validate', {})
		field_info = getattr(self.Meta, 'field_info', {})
		
		for name, field in self.fields.items():
			newattrs = {}
			if isinstance(field, (DateField,)):
				newattrs.update({'class' : 'datepicker placeholder', 'title' : 'YYYY-mm-dd'})
				
				if hasattr(field, 'min_date_range'):
					newattrs.update({'data-min_date_range' : field.min_date_range.strftime("%Y/%m/%d")})
			
			if isinstance(field, forms.DecimalField):
				field.localize = True
				field.widget.is_localized = True
			
			if HTML5_WIDGETS.get('email', False) and isinstance(field, forms.EmailField): 
				field.widget.input_type = 'email'
			
			if HTML5_WIDGETS.get('number', False) and isinstance(field, forms.IntegerField):
				field.widget.input_type = 'number'
				
				if field.max_value is not None:
					newattrs.update({'max' : field.max_value})
				
				if field.min_value is not None:
					newattrs.update({'min' : field.min_value})
				
			if validate.has_key(name):
				validate_string = validate[name]
				newattrs.update({'data-validate' : validate_string})
			
			if field_info.has_key(name):
				info = field_info[name]
				
				field_data = info.pop('data', {})
				
				newattrs.update(info)
				
				for key, value in field_data.items():
					key = "data-{}".format(key)
					newattrs.update({ key : value})
				
				# re-add data back into the meta
				info['data'] = field_data
			
			field.widget.attrs.update(newattrs)
		
	# A default Meta class that can be used in any subclass
	class Meta(object): pass

class Form(BaseFormMixin, forms.Form):
	
	def _html_output(self, *args, **kwargs):
		return jinja2.Markup(super(Form, self)._html_output(*args, **kwargs))
	
	def __html__(self):
		return self.as_table()

class ModelForm(BaseFormMixin, forms.ModelForm):
	template_module = jinja_env.get_template('asymmetricbase/forms/form_rows.djhtml').module
	
	def _html_output(self, *args, **kwargs):
		
		return jinja2.Markup(super(ModelForm, self)._html_output(*args, **kwargs))
	
	def _render_html_template(self, template_macro, errors_on_separate_row, required_mark = '*'):
		top_errors = self.non_field_errors()
		output, hidden_fields = [], []
		
		for name, field in self.fields.items():
			macro_args = {
				'label' : '',
				'field' : unicode(field),
				'help_text' : '',
				'errors' : '',
				'html_class_attr' : '',
				'is_error_row' : errors_on_separate_row,
				'required_mark' : ''
			}
			
			bf = self[name]
			bf_errors = self.error_class([conditional_escape(error for error in bf.errors)])
			macro_args['errors'] = force_unicode(bf_errors)
			
			macro_args['required_mark'] = required_mark if field.required else u''
			
			if bf.is_hidden:
				if bf.errors:
					top_errors.extend([u'(Hidden field {}) {}'.format(name, force_unicode(e)) for e in bf_errors])
				hidden_fields.append(unicode(bf))
			
			else:
				css_classes = bf.css_classes()
				if css_classes:
					macro_args['html_class_attr'] = ' class="{}"'.format(css_classes)
				
				if errors_on_separate_row and bf_errors:
					output.append(template_macro(**macro_args))
				
				if bf.label:
					label = conditional_escape(force_unicode(bf.label))
					
					if self.label_suffix:
						if label[-1] not in ':?.!':
							label += self.label_suffix
							
					label_css = 'required' if field.required else u''
					
					macro_args['label'] = bf.label_tag(label, attrs = {'class' : label_css}) or u''
					
				else:
					macro_args['label'] = u''
				
				if field.help_text:
					macro_args['help_text'] = force_unicode(field.help_text)
				else:
					macro_args['help_text'] = u''
				
				output.append(template_macro(**macro_args))
			
		if top_errors:
			output.insert(0, template_macro(label = '', field = '', help_text = '', html_class_attr = '', is_error_row = True, errors = top_errors))
		
		if hidden_fields:
			output.append(u''.join(hidden_fields))
		
		return jinja2.Markup(output)
	
	def as_table(self):
		return self._render_html_template(self.template_module.as_table, False)
	
	def as_tr(self):
		return '<tr>{}</tr>'.format(self._render_html_template(self.template_module.as_tr, False))
	
	def as_ul(self):
		return self._render_html_template(self.template_module.as_ul, False)
	
	def as_p(self):
		return self._render_html_template(self.template_module.as_p, True)
		
	def is_valid_and_save(self, commit = True):
		if self.is_valid():
			return self.save(commit)
		
		return False

class TwoColumnTableLayout(object):
	"""
	This is basically a class to override the default as_table function.
	Note that this does NOT inherit from forms.(Model)Form since we don't
	want to override any other methods/attributes.
	To use this form, in the inheritance list, it must come before any other 
	classes that implement the as_table() method to take advantage of C3 MRO
	"""
	def as_table(self):
		return self._render_html_template(self.template_module.as_table_twocol, False)

class AsymBaseModelFormSet(BaseModelFormSet):
	
	def is_valid_and_save(self, commit = True):
		if self.is_valid():
			return self.save(commit)
		
		return False

def make_modelformset_factory(model, form = ModelForm, *args, **kwargs):
	formargs = kwargs.pop('formargs', {})
	exclude = kwargs.pop('exclude', ())
	kwargs.setdefault('formset', AsymBaseModelFormSet)
	
	class WrapperClass(form):
		def __init__(self, *args, **kwargs):
			kwargs.update(formargs)
			super(WrapperClass, self).__init__(*args, **kwargs)
			
			for fname in exclude:
				del self.fields[fname]
	
	kwargs.update(dict(form = WrapperClass))
	return modelformset_factory(model, *args, **kwargs)


monkey_patch_django()
