"""
Copyright (C) 2010 Appropriate Solutions, Inc., all rights reserved.
This code is released to be used under the terms of the Apache license, by
Bill Freeman, for Appropriate Solutions, Inc., www.appropriatesolutions.com
Radio-Iterator Feature: Copyright (C) 2010 Andreas Pfrengle

NOTE: This code takes advantage of django internal interfaces.
  Such are subject to change in new django versions, making this
  code invalid.  It was developed and tested for a Django 1.0.3
  (pinax) based site.  I make no presentation that this stuff
  will work on any other version, or even this version with a
  different set of apps or versions.  But it should be close.
  Your milage may vary.

  Checkbox-iterator was also tested under Django 1.2.1. Seems to work...
  Radio-Iterator was developed under Django 1.2.1.
  
  
  - (reames 20/9/12): Allow the choices to have access to the model they represent

HOW TO USE:
  copy this code into my_app/templatetags/fielditerator.py
	(__init__.py has also to be present). See also:
	<http://docs.djangoproject.com/en/1.2/howto/custom-template-tags/#code-layout>
  forms.py: Define a form with my_field = ChoiceField, TypedChoiceField or
	MultipleChoiceField and widget=RadioSelect or CheckboxSelectMultiple.
	(setting the widget is necessary if you wish e.g. a TypedChoiceField
	with multi-select feature, otherwise you don't need to specify it,
	since the template-filters in this file decide upon the used widget)
  Usage 1 (just get the widgets in a template for-loop):
	template.html:
	  {% load fielditerator %} <!-- then use the templatefilters like -->
	  {% for button in my_form.my_field|radioiterator_named %}
	  Each {{button}} is a labeled html radiobutton-input with choice-text displayed
  Usage 2 (zip the widgets with other data you want inside the template's for-loop):
	views.py:
	  import my_app.templatetags.fielditerator
	  buttons = [b for b in fielditerator.radioiterator_named(my_form['my_field'])]
		  #my_form['my_field'] calls forms.BaseForm.__getitem__, returns a BoundField
	  data = {'form_data': zip(other_data_iterable, buttons)}
	  return render_to_response('template.html', RequestContext(request, data))
	template.html:
	  {% for data, button in form_data %} #do your stuff with data, 'annotated' with buttons...
"""
from django import template
from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.forms.util import flatatt
import django.forms


register = template.Library()

class _RadioInput(django.forms.widgets.RadioInput):
	"""
	Overrides part of Django's RadioInput widget. Since RadioInput is usually
	called from the RadioSelect widget's renderer, it has no own "render"-method.
	This is implemented here.
	Also, the "tag"-method needs to be adjusted, so it doesn't append
	"_0", "_1" etc. to the id (this is already done in the "_iterator" function).
	"""
	def __init__(self, name, value, attrs, choice, index, checked):
		super(_RadioInput, self).__init__(name, value, attrs, choice, index)
		self.checked = checked

	def tag(self):
		final_attrs = dict(self.attrs, type = 'radio', name = self.name, value = self.choice_value)
		if self.checked:	#This line is different from parent classes "tag"
			final_attrs['checked'] = 'checked'
		return mark_safe(u'<input%s />' % flatatt(final_attrs))

	def render(self):
		"""Outputs the <input> for this radio field"""
		return mark_safe(u'%s' % force_unicode(self.tag()))



class _PseudoBoundField(object):
	"""An object from which to render one checkbox or radio button.

	Helper class.

	Because the checkbox iterator needs to be able return something
	that acts, closely enough, like a checkbox bound field.
	"""
	def __init__(self, name, option_label, option_value, attrs, checked, display_name, extra = None):
		self.parent_name = name
		self.name = option_label
		self.display_name = display_name
		self.value = option_value
		self.attrs = attrs
		self.checked = checked
		self.id = attrs.get('id', '')
		self.errors = u'' # We don't have individual cb errors
		self.extra = extra

	def label_head(self):
		if not self.id:
			return u'<label>'
		return mark_safe(u'<label for="%s">' % self.id)

	def labeled(self):
		name = u''
		if self.display_name:
			name = self.name
		return mark_safe(u'%s%s %s</label>' % (
			self.label_head(),
			self.tag(),
			name
			))

	def lone_label(self):
		return mark_safe(u'%s%s</label>' % (
			self.label_head(),
			self.name
			))

	def __unicode__(self):
		return self.labeled()

class _PseudoCheckboxBoundField(_PseudoBoundField):
	def __init__(self, *args, **kwargs):
		kwargs.pop('radio_id')   #item not needed for Checkbox, remove it
		super(_PseudoCheckboxBoundField, self).__init__(*args, **kwargs)

	def tag(self):
		cb = django.forms.CheckboxInput(self.attrs, check_test = lambda v: self.checked)
		return cb.render(self.parent_name, self.value)

class _PseudoRadioBoundField(_PseudoBoundField):
	def __init__(self, *args, **kwargs):
		self.radio_id = kwargs.pop('radio_id')
		super(_PseudoRadioBoundField, self).__init__(*args, **kwargs)

	def tag(self):
		choice = (self.value, self.name)
		radio = _RadioInput(self.parent_name, self.value, self.attrs, choice,
													self.radio_id, self.checked)
		return radio.render()



class _ValueGrabber(object):
	"""A pseudo widget to capture information from the MultiSelect object.

	This is a helper class.

	There's no clean way to reach into the MultiSelect bound field to
	get this information, but it does call its widget with all the
	necessary info.  This probably has legs because changing the
	render interface would have far reaching consequences.
	"""
	def __init__(self):
		self.attrs = {}

	def render(self, name, data, attrs):
		self.name = name
		self.data = data
		self.attrs = attrs

def _iterator(bound_field, widget_type, display_name):
	"""
	Generator that yields the html of the bound field's choices
	as checkboxes or radio buttons.
	This is achieved by returning _PseudoBoundField-instances.
	"""
	widget = bound_field.field.widget
	# Snag the bound field details.  Let it's as_widget method do the work.
	bfd = _ValueGrabber()
	bound_field.as_widget(bfd)
	name = bfd.name
	values = bfd.data
	attrs = bfd.attrs

	# Fix up data and attrs
	if values is None:
		values = set()
	elif type(values) is list:
		values = set([force_unicode(v) for v in values])
	else:
		values = set([force_unicode(values)])

	widget_id = attrs and attrs.get('id', False)
	partial_attrs = widget.build_attrs(attrs, name = name)

	for i, (option_value, option_label) in enumerate(widget.choices):
		extra = None
		if isinstance(option_value, (list, tuple)):
			extra, option_value = option_value
		option_value = force_unicode(option_value)
		final_attrs = partial_attrs
		if widget_id is not False:
			final_attrs = dict(partial_attrs,
							   id = u'%s_%s' % (widget_id, i))
		yield widget_type(
			name = name,
			option_label = conditional_escape(force_unicode(option_label)),
			option_value = option_value,
			attrs = final_attrs,
			checked = option_value in values,
			display_name = display_name,
			radio_id = i,
			extra = extra
		)

#@register.filter
def checkboxiterator(bound_field):
	"""
	Use this method on MultiSelect fields. return iterator of:
	<label for="id_my_field_x"><input type="checkbox" name="my_field"
		value="abc" id="id_my_field_x" /> </label>
	"""
	return _iterator(bound_field, _PseudoCheckboxBoundField, display_name = False)

#@register.filter
def checkboxiterator_named(bound_field):
	"""
	Same as checkboxiterator, but also displays the choice's text:
	<label for="id_my_field_x"><input type="checkbox" name="my_field"
		value="abc" id="id_my_field_x" /> choice-text</label>
	"""
	return _iterator(bound_field, _PseudoCheckboxBoundField, display_name = True)

#@register.filter
def radioiterator(bound_field):
	"""
	Use this method on Single-value fields. return iterator of:
	<label for="id_my_field_x"><input type="radio" name="my_field"
		value="abc" id="id_my_field_x" /> </label>
	"""
	return _iterator(bound_field, _PseudoRadioBoundField, display_name = False)

#@register.filter
def radioiterator_named(bound_field):
	"""
	Same as radioiterator, but also displays the choice's text:
	<label for="id_my_field_x"><input type="radio" name="my_field"
		value="abc" id="id_my_field_x" /> choice-text</label>
	"""
	return _iterator(bound_field, _PseudoRadioBoundField, display_name = True)
