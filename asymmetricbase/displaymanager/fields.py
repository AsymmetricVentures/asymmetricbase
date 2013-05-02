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

from functools import total_ordering

from jinja2.utils import contextfunction

@total_ordering
class DisplayField(object):
	creation_counter = 0
	
	def __init__(self, header_name = None):
		self.header_name = header_name
		self.attrname = ''
		self.model = None
		
		self.creation_counter = DisplayField.creation_counter
		DisplayField.creation_counter += 1
	
	def contribute_to_class(self, cls, name):
		self.attrname = name
		self.model = cls
		
		if self.header_name is None:
			self.header_name = name.replace('_', ' ').title()
		
		if hasattr(cls, '_meta'):
			cls._meta.add_field(self)
	
	def __str__(self):
		return str(getattr(self.model, self.name))
	
	def __hash__(self):
		return hash((type(self), self.model, self.attrname, self.creation_counter))
	
	def __eq__(self, other):
		return self.creation_counter == other.creation_counter
	
	def __lt__(self, other):
		return self.creation_counter < other.creation_counter

class AttrGetField(DisplayField):
	""" Can be used in 1 of two ways
	    First, in a display of the form:
	      attr_name = dm.AttrGetField()
	    will display `obj.attr_name`
	    
	    Second, in a display of the form:
	      name = dm.AttrGetField(attr='nested.attribute')
	    will display `obj.nested.attribute`
	"""
	def __init__(self, header_name = None, attr = None, *args, **kwargs):
		super(AttrGetField, self).__init__(header_name)
		self.attr = attr
	
	@contextfunction
	def __call__(self, context, instance):
		return self.attr_field_macro(context = context)(instance, attr = self.field_name)
	
	def attr_field_macro(self, context = {}):
		return self.model.get_macro('attr_field', context = context)
	
	@property
	def field_name(self):
		return self.attr if self.attr is not None else self.attrname

class AttrCallField(AttrGetField):
	"""
	Same as AttrGetField except that it calls the field.
	"""
	def attr_field_macro(self, context = {}):
		return self.model.get_macro('attr_call_field', context = context)

class TemplateField(DisplayField):
	"""
	Renders using the macro defined in macro_name.
	
	Can be given additional positional or keyword arguments, which will be passed
	to the macro if the macro supports varargs or kwargs (see jinja2 docs).
	"""
	def __init__(self, header_name = None, macro_name = '', *args, **kwargs):
		self.macro_name = macro_name
		self.args = args
		self.kwargs = kwargs
		super(TemplateField, self).__init__(header_name)
	
	def template_macro(self, context = {}):
		return self.model.get_macro(self.macro_name, context = context)
	
	@contextfunction
	def __call__(self, context, instance):
		return self.template_macro(context)(instance, *self.args, **self.kwargs)

class AutoTemplateField(TemplateField, AttrGetField):
	
	def __init__(self, *args, **kwargs):
		macro_name = self.__class__.__name__.lower()
		# We're calling the supers separately because otherwise c3 doesn't 
		# get to the second super.
		TemplateField.__init__(self, macro_name = macro_name, *args, **kwargs)
		AttrGetField.__init__(self, *args, **kwargs)
	
	@contextfunction
	def __call__(self, context, instance):
		return TemplateField.__call__(self, context, AttrGetField.__call__(self, context, instance))

class AttrTemplateField(TemplateField):
	"""
	Renders obj.attr using a given macro
	"""
	
	def __init__(self, header_name = None, *args, **kwargs):
		self.attr = kwargs.pop('attr', None)
		super(AttrTemplateField, self).__init__(header_name, *args, **kwargs)
		
	@contextfunction
	def __call__(self, context, instance):
		other_macro = self.template_macro(context)
		return self.model.get_macro('attr_template_field', context = context)(instance, other_macro = other_macro, attr = self.attr)
		
		

class LinkField(AutoTemplateField):
	'''
	'''
	def __init__(self, header_name = None, url_name = '', use_instance = False, *args, **kwargs):
		macro_name = kwargs.pop('macro_name', None)
		self.url_name = url_name
		self.use_instance = use_instance
		super(LinkField, self).__init__(*args, **kwargs)
		
		if macro_name is not None:
			self.macro_name = macro_name
	
	@contextfunction
	def __call__(self, context, instance):
		macro = self.template_macro(context = context)
		if self.use_instance:
			return macro(instance, self.url_name, *self.args, **self.kwargs)
		else:
			return macro(AttrGetField.__call__(self, context, instance), self.url_name, *self.args, **self.kwargs)

class IntField(AutoTemplateField): pass
class CharField(AutoTemplateField): pass

class ContextField(): pass

class GridLayoutField(TemplateField):
	
	def __init__(self, *args, **kwargs):
		self.row = 'row-' + str(kwargs.pop('row', 0))
		self.col = 'col-' + str(kwargs.pop('col', 0))
		self.rowspan = kwargs.pop('rowspan', 1)
		self.colspan = kwargs.pop('colspan', 1)
		super(GridLayoutField, self).__init__(*args, **kwargs)

class NestedTemplateField(TemplateField):
	
	def __init__(self, header_name = None, macro_name = '', child_name = None, root = False, *args, **kwargs):
		self.child_name = child_name
		self.child = None
		self.root = root
		
		super(NestedTemplateField, self).__init__(header_name, macro_name, *args, **kwargs)
	
	@contextfunction
	def __call__(self, context, instance):
		return self.template_macro(context = context)(instance, self.child, *self.args, **self.kwargs)

class MenuItemField(TemplateField):
	
	def __init__(self, header_name = '', macro_name = 'linkfield', *args, **kwargs):
		super(MenuItemField, self).__init__(header_name, macro_name, *args, **kwargs)
	
	@contextfunction
	def __call__(self, context, instance):
		if not isinstance(instance, MenuItem):
			raise TypeError('MenuItemField must be called on an instance of MenuItem')
		kwargs = {}
		kwargs['url_kwargs'] = instance.kwargs
		kwargs['url_args'] = instance.args
		kwargs['url_text'] = instance.label
		kwargs['get_args'] = instance.url_args
		return self.template_macro(context = context)(instance, url_name = instance.url, **kwargs)

class MenuItem(object):
	"""
	Encapsulates a menu item for use with MenuDisplay.
	
	If the args or kwargs cannot be resolved now (IE we need to wait on a form or callback)
	pass them in wrapped in lambda functions, as they can be resolved using
	process_arguments() later.
	"""
	
	def __init__(self, url = None, label = '', url_args = None, *args, **kwargs):
		self.url = url
		self.label = label
		self.url_args = url_args
		self.args = args
		self.kwargs = kwargs
	
	def process_arguments(self):
		"""
		Check if any argument in self.args or self.kwargs is callable
		(IE lambda functions) and call any that are.
		"""
		
		new_args = []
		for arg in self.args:
			if callable(arg):
				new_args.append(arg())
			else:
				new_args.append(arg)
		self.args = tuple(new_args)
		
		for k, v in self.kwargs.items():
			if callable(v):
				v = v()
			self.kwargs.update({
				k : v
			})
		
		if callable(self.url_args):
			self.url_args = self.url_args()
