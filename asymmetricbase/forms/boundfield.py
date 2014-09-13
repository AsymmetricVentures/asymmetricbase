# -*- coding: utf-8 -*-
#    Asymmetric Base Framework - A collection of utilities for django frameworks
#    Copyright (C) 2013  Asymmetric Ventures Inc.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; version 2 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from __future__ import absolute_import, division, print_function, unicode_literals

import sys

from django.forms import forms
from django.forms.utils import flatatt
from django.utils.functional import cached_property
from django.utils.encoding import force_text
from django.dispatch import Signal
from django.utils.html import conditional_escape, format_html

from asymmetricbase.jinja import jinja_env

boundfield_props = Signal()

class BoundLabel:
	def __init__(self, bound_field, field, form, **kwargs):
		self.bound_field = bound_field
		self.field = field
		self.form = form
		self.attrs = kwargs
		super(BoundLabel, self).__init__()
	
	def attr(self, name, value = None):
		self.attrs[name] = value
		return self
	
	def append_classes(self, *values):
		current = set(self.attrs.get('class', '').split(' '))
		current.update(values)
		self.attrs['class'] = ' '.join(current)
		return self
	
	def render(self):
		contents = self.attrs.pop('contents', None)
		if contents is None:
			contents = self.bound_field.label
		label_suffix = self.attrs.pop('label_suffix', None)
		if label_suffix is None:
			label_suffix = self.form.label_suffix
		if label_suffix and contents and contents[-1] not in ':?.!':
			contents = format_html('{}{}'.format(contents, label_suffix))
		widget = self.field.widget
		id_ = widget.attrs.get('id') or self.bound_field.auto_id
		if id_:
			id_for_label = widget.id_for_label(id_)
			if id_for_label:
				attrs = dict(self.attrs or {}, **{'for' : id_for_label})
			attrs = flatatt(attrs) if attrs else ''
		else:
			contents = conditional_escape(contents)
		return format_html(
			'<label{}>{}</label>', attrs, contents
		)
	
	def __str__(self):
		return self.render()

class BoundField(forms.BoundField):
	@cached_property
	def template_module(self):
		return jinja_env.get_template('asymmetricbase/boundfield/default.djhtml').module
	
	def _get_fields(self):
		if self.is_hidden:
			return self
		
		if self.label:
			label = conditional_escape(force_text(self.label))
			
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
	
	def label_tag(self, contents = None, attrs = None, label_suffix = None):
		if attrs is None:
			attrs = {}
		attrs.setdefault('contents', contents)
		return BoundLabel(
			bound_field = self, field = self.field, form = self.form,
			label_suffix = label_suffix, **attrs
		)
	
	just_field = property(lambda self: self._render_with_template('just_field'))
	
	vseg = property(lambda self: self._render_with_template('vblock_segment'))
	hseg = property(lambda self: self._render_with_template('hblock_segment'))
	rhseg = property(lambda self: self._render_with_template('rhblock_segment'))
	
	bs = property(lambda self: self._render_with_template('bootstrap_default'))
	bs_inline = property(lambda self: self._render_with_template('bootstrap_inline'))
	bs_h = property(lambda self: self._render_with_template('bootstrap_horizontal'))
	
	bs3 = property(lambda self: self._render_with_template('bootstrap3_default'))
	bs3_inline = property(lambda self: self._render_with_template('bootstrap3_inline'))
	bs3_h = property(lambda self: self._render_with_template('bootstrap3_horizontal'))
	bs3_field = property(lambda self: self._render_with_template('bs3_field'))
	# methods to replace django widget_tweaks
	
	def _process_attributes(self, name, value, process):
		
		widget = self.field.widget
		attrs = getattr(widget, 'attrs', {})
		
		process(widget, attrs, name, value)
	
	def attr(self, name, value):
		def process(widget, attrs, name, value):
			attrs[name] = value
		self._process_attributes(name, value, process)
		
		return self
	
	def append_attr(self, name, value):
		def process(widget, attrs, name, value):
			if attrs.get(name):
				attrs[name] += ' ' + value
			else:
				attrs[name] = value
		self._process_attributes(name, value, process)
		
		return self
	
	def add_class(self, value):
		return self.append_attr('class', value)
	
	def add_error_class(self, value):
		if hasattr(self.field, 'errors') and self.field.errors:
			return self.add_class(value)
		return self
	
	def set_data(self, name, value):
		return self.attr('data-' + name, value)
	
	
setattr(sys.modules['django.forms.forms'], 'BoundField', BoundField)

# Give other parts of the code a chance to register custom functions on boundfield
boundfield_props.send(sender = BoundField)

