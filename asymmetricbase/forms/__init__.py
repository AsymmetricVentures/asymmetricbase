from django.forms import * #@UnusedWildImport pylint: disable-msg=W0401
from django import forms #@Reimport
from django.forms.models import modelformset_factory, BaseModelFormSet
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.conf import settings

import jinja2

from asymmetricbase.forms.boundfield import BoundField

HTML5 = getattr(settings, 'ASYM_HTML5', False)
HTML5_WIDGETS = getattr(settings, 'ASYM_HTML5_WIDGETS',  {})

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
		try:
			self.Meta
		except AttributeError:
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
			
			if HTML5_WIDGETS.get('email', False) and isinstance(field, forms.EmailField): # Jayson global accepts 'na' in their email input
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
		

class Form(BaseFormMixin, forms.Form):
	
	def _html_output(self, *args, **kwargs):
		return jinja2.Markup(super(Form, self)._html_output(*args, **kwargs))

class ModelForm(BaseFormMixin, forms.ModelForm):
	
	def _html_output(self, normal_row, error_row, row_ender, help_text_html, errors_on_separate_row, required_mark, surround = None):
		"Helper function for outputting HTML. Used by as_table(), as_ul(), as_p()."
		top_errors = self.non_field_errors() # Errors that should be displayed above all fields.
		output, hidden_fields = [], []
		
		for name, field in self.fields.items():
			html_class_attr = ''
			bf = BoundField(self, field, name)
			bf_errors = self.error_class([conditional_escape(error) for error in bf.errors]) # Escape and cache in local variable.
			
			local_required_mark = required_mark
			
			if not field.required:
				local_required_mark = ''
			
			if bf.is_hidden:
				if bf_errors:
					top_errors.extend([u'(Hidden field %s) %s' % (name, force_unicode(e)) for e in bf_errors])
				hidden_fields.append(unicode(bf))
			else:
				# Create a 'class="..."' attribute if the row should have any
				# CSS classes applied.
				css_classes = bf.css_classes()
				if css_classes:
					html_class_attr = ' class="%s"' % css_classes
				
				if errors_on_separate_row and bf_errors:
					output.append(error_row % force_unicode(bf_errors))
				
				if bf.label:
					label = conditional_escape(force_unicode(bf.label))
					# Only add the suffix if the label does not end in
					# punctuation.
					if self.label_suffix:
						if label[-1] not in ':?.!':
							label += self.label_suffix
					
					
					label_css = 'required' if field.required else ''
					
					label = bf.label_tag(label, attrs = {'class':label_css}) or ''
				else:
					label = ''
				
				if field.help_text:
					help_text = help_text_html % force_unicode(field.help_text)
				else:
					help_text = u''
				
				output.append(normal_row % {
					'errors': force_unicode(bf_errors),
					'label': force_unicode(label),
					'field': unicode(bf),
					'help_text': help_text,
					'html_class_attr': html_class_attr,
					'required_mark' : local_required_mark,
				})
		
		if top_errors:
			output.insert(0, error_row % force_unicode(top_errors))
		
		if hidden_fields: # Insert any hidden fields in the last row.
			str_hidden = u''.join(hidden_fields)
			if output:
				last_row = output[-1]
				# Chop off the trailing row_ender (e.g. '</td></tr>') and
				# insert the hidden fields.
				if not last_row.endswith(row_ender):
					# This can happen in the as_p() case (and possibly others
					# that users write): if there are only top errors, we may
					# not be able to conscript the last row for our purposes,
					# so insert a new, empty row.
					last_row = (normal_row % {'errors': '', 'label': '',
											  'field': '', 'help_text':'',
											  'html_class_attr': html_class_attr,
											  'required_mark' : required_mark,
											 })
					output.append(last_row)
				output[-1] = last_row[:-len(row_ender)] + str_hidden + row_ender
			else:
				# If there aren't any rows in the output, just append the
				# hidden fields.
				output.append(str_hidden)
		
		output = u'\n'.join(output)
		
		if isinstance(surround, basestring):
			output = surround % output
		
		return jinja2.Markup(output)
	
	def as_table(self):
		return self._html_output(
			normal_row = u'''<tr%(html_class_attr)s>
				<th>%(required_mark)s%(label)s</th>
				<td>%(field)s%(errors)s%(help_text)s</td></tr>\n''',
			error_row = u'<tr><td colspan="2">%s</td></tr>\n',
			row_ender = u'</td></tr>\n',
			help_text_html = u'<span class="help-text"><br />%s</span>',
			errors_on_separate_row = False,
			required_mark = '<span class="required-marker">* </span>'
			)
	
	def as_table_row(self):
		return self._html_output(
			normal_row = '<td%(html_class_attr)s>%(field)s%(errors)s%(help_text)s</td>\n',
			error_row = '<br /><span>%s</span>\n',
			row_ender = '</td>\n',
			help_text_html = '<br/><span class="help-text>%s</span>\n',
			errors_on_separate_row = False,
			required_mark = '',
			surround = '<tr>%s</tr>'
		)
		
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
		return self._html_output(
			normal_row = u'''<tr%(html_class_attr)s>
				<th>%(label)s</th>
				<td>%(field)s%(required_mark)s%(errors)s%(help_text)s</td></tr>\n''',
			error_row = u'<tr><td colspan="2">%s</td></tr>\n',
			row_ender = u'</td></tr>\n',
			help_text_html = u'<span class="help-text"><br />%s</span>',
			errors_on_separate_row = False,
			required_mark = '<span class="required-marker"> *</span>'
		)

class MyBaseModelFormSet(BaseModelFormSet):
	
	def is_valid_and_save(self, commit = True):
		if self.is_valid():
			return self.save(commit)
		
		return False

def make_modelformset_factory(model, form = ModelForm, *args, **kwargs):
	formargs = kwargs.pop('formargs', {})
	exclude = kwargs.pop('exclude', ())
	
	class WrapperClass(form):
		def __init__(self, *args, **kwargs):
			kwargs.update(formargs)
			super(WrapperClass, self).__init__(*args, **kwargs)
			
			for fname in exclude:
				del self.fields[fname]		
	
	kwargs.update(dict(form = WrapperClass))	
	return modelformset_factory(model, formset = MyBaseModelFormSet, *args, **kwargs)


monkey_patch_django()
