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

from bisect import bisect
from collections import OrderedDict

from django.core.exceptions import FieldError

from jinja2.runtime import Macro
from jinja2.utils import contextfunction

from asymmetricbase.jinja import jinja_env
from asymmetricbase.utils.orderedset import OrderedSet
from asymmetricbase.middleware.request_cache import get_request_cache

DEFAULT_NAMES = ('ordering', 'structural_name',)

class DisplayOptions(object):
	def __init__(self, meta):
		self.meta = meta
		self.local_fields = []
		self.ordering = []
		self.template_name = OrderedSet()
		self.structural_name = []
		self.concrete_model = None
		self.parents = OrderedDict()
	
	def contribute_to_class(self, cls, name):
		cls._meta = self
		
		if self.meta:
			meta_attrs = self.meta.__dict__.copy()
			for name in self.meta.__dict__:
				if name.startswith('_'):
					del meta_attrs[name]
			
			# special case template_name because it's an orderedset
			if 'template_name' in meta_attrs:
				template_names = meta_attrs.pop('template_name')
			elif hasattr(self.meta, 'template_name'):
				template_names = self.meta.template_name
			
			if isinstance(template_names, (list, tuple, OrderedSet, set)):
				self.template_name.update(template_names)
			else:
				self.template_name.add(template_names)
			
			for attr_name in DEFAULT_NAMES:
				if attr_name in meta_attrs:
					setattr(self, attr_name, meta_attrs.pop(attr_name))
				elif hasattr(self.meta, attr_name):
					setattr(self, attr_name, getattr(self.meta, attr_name))
			
			if meta_attrs != {}:
				raise TypeError("'class Meta' got invalid attribute(s): {}".format(','.join(meta_attrs.keys())))
		
		del self.meta
	
	def add_field(self, field):
		self.local_fields.insert(bisect(self.local_fields, field), field)
		if hasattr(self, '_field_cache'):
			del self._field_name_cache
			del self._field_cache
	
	def _prepare(self, model): pass
	
	@property
	def fields(self):
		try:
			self._field_name_cache
		except AttributeError:
			self._fill_fields_cache()
		return self._field_name_cache
	
	def get_fields_with_model(self):
		try:
			self.field_cache
		except AttributeError:
			self._fill_fields_cache()
		return self.field_cache
	
	def _fill_fields_cache(self):
		cache = []
		
		for parent in self.parents:
			for field, model in parent._meta.get_fields_with_model():
				if model:
					cache.append((field, model))
				else:
					cache.append((field, parent))
		cache.extend(((f, None) for f in self.local_fields))
		self.field_cache = tuple(cache)
		self._field_name_cache = [x for x, _ in cache]
	
class DisplayMeta(type):
	
	@staticmethod
	def _load_templates(template_dict, template_name):
#		if template_name is not None:
#			if isinstance(template_name, (list, tuple, OrderedSet)):
#				for name in template_name:
#					#if name not in template_dict:
#						#TODO: this needs to be lazy
#						#template_dict.update({name : jinja_env.get_template(name).module})
#			else:
#				if template_name not in template_dict:
#					template_dict.update({template_name : jinja_env.get_template(template_name).module})
#		
		return template_dict
	
	def __new__(cls, name, bases, attrs):
		parents = [b for b in bases if isinstance(b, DisplayMeta)]
		
		# Create the class.
		module = attrs.pop('__module__')
		new_class = super(DisplayMeta, cls).__new__(cls, name, bases, {'__module__': module})
		attr_meta = attrs.pop('Meta', None)
		if not attr_meta:
			meta = getattr(attr_meta, 'Meta', None)
		else:
			meta = attr_meta
		
		# base_meta = getattr(new_class, '_meta', None)
		
		new_class.add_to_class('_meta', DisplayOptions(meta))
		
		for obj_name, obj in attrs.items():
			new_class.add_to_class(obj_name, obj)
		
		new_fields = new_class._meta.local_fields
		field_names = set([f.attrname for f in new_fields])
		
		new_class._meta.concrete_model = new_class
		
		for base in parents:
			if not hasattr(base, '_meta'):
				continue
			parent_meta = base._meta
			parent_fields = parent_meta.local_fields
			
			for field in parent_fields:
				if field.attrname in field_names:
					raise FieldError('Local Field {!r} in class {!r} clashes with field of similar name from base class {!r}'.format(field.attrname, name, base.__name__))
			
			# new_class._meta.template_name is always going to be an OrderedSet
			# because DisplayOptions always sets it as one.
			new_class._meta.template_name.update(parent_meta.template_name)
			
			new_class._meta.parents[base] = base
		
		# build template dictionary
		#template_dict = DisplayMeta._load_templates(OrderedDict(), getattr(new_class._meta, 'template_name', None))
		
		new_class.template_dict = OrderedDict()
		
		new_class._prepare()
		
		return new_class
	
	def _prepare(cls): # @NoSelf
		opts = cls._meta
		opts._prepare(cls)
		
		if cls.__doc__ is None:
			cls.__doc__ = '{}({})'.format(cls.__name__, ', '.join([f.attrname for f in opts.fields]))
	
	def add_to_class(cls, name, value): # @NoSelf
		if hasattr(value, 'contribute_to_class'):
			value.contribute_to_class(cls, name)
		else:
			setattr(cls, name, value)

class Display(object):
	''' Per "model" '''
	__metaclass__ = DisplayMeta
	
	USE_CACHE = False
	
	def __init__(self, obj, *args, **kwargs):
		self.obj = obj
	
	def __str__(self):
		return self.__html__()
	
	def __html__(self):
		return self.__call__()
	
	@contextfunction
	def __call__(self, context = {}):
		return self.get_macro('display', context = context)(self)
		
	@classmethod
	def get_macro(cls, name, **kwargs):
		"""Get a macro by name and context
		"""
		context = kwargs.pop('context', {})
		
		if Display.USE_CACHE:
			if id(context) == id({}):
				tmp = {}
				tmp = context
				context = {}
				context = tmp
			
			
			cache = get_request_cache()
			
			macro_key = Display.__make_key(id(cls), name, id(context))
			
			macro_ret = cache.get(macro_key)
		else:
			macro_ret = None
		
		if macro_ret is None:
			# Load all macros with this context
			template_dict = Display._load_templates(OrderedDict(), getattr(cls._meta, 'template_name', None), context)
			
			# Now find all the macros
			for template_module in reversed(template_dict.values()):
				for macro_name, macro in template_module.__dict__.items():
					if isinstance(macro, Macro):
						if macro_name == name:
							macro_ret = macro
						if Display.USE_CACHE:
							cache.set(Display.__make_key(id(cls), macro_name, id(context)), macro)
		
		if macro_ret is None:
			raise AttributeError('Cannot get macro \'{}\''.format(name))
		
		return macro_ret
	
	@staticmethod
	def __make_key(*args):
		return '-'.join(map(str, args))
	
	@staticmethod
	def _load_templates(template_dict, template_name, context):
		if template_name is not None:
			if isinstance(template_name, (list, tuple, OrderedSet)):
				for name in template_name:
					if name not in template_dict:
						template_dict.update({name : jinja_env.get_template(name, globals = context).module})
			else:
				if template_name not in template_dict:
					template_dict.update({template_name : jinja_env.get_template(template_name, globals = context).module})
		
		return template_dict
