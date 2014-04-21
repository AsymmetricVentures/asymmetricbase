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

from django.forms.models import BaseModelFormSet

class BaseNestedFormSet(BaseModelFormSet):
	
	nested_att_name = 'nested'
	
	def __init__(self, *args, **kwargs):
		"""
		Request is passed into this formset so it can be passed down into
		any nested formsets (since these need the request data on initialization).
		"""
		self.request = kwargs.pop('request', None)
		if self.request is None:
			raise Exception('request object must be passed to formset via argument to FactoryFactory')
		super(BaseNestedFormSet, self).__init__(*args, **kwargs)
	
	def add_fields(self, form, index):
		# allow the superclass to add fields as usual
		super(BaseNestedFormSet, self).add_fields(form, index)
		
		try:
			instance = self.get_queryset()[index]
			pk_value = instance.pk
		except IndexError:
			instance = None
			# TODO: not sure about the uniqueness of this. hash(form) might be better
			pk_value = hash(form.prefix)
		
		# define a formset
		nested_formset_factory_factory = self._generate_formset(self.request, instance, pk_value)
		
		# set the name of the attribute where the formset is nested
		form.nested_attr_name = self.nested_att_name
		# nest the next formset
		setattr(form, form.nested_attr_name, nested_formset_factory_factory(self.request))
	
	def _generate_formset(self, request, instance, pk_value):
		"""
		Returns an instance of FormSetFactoryFactory
		(or ModelFormSetFactoryFactory, or InlineFormSetFactoryFactory)
		that should be used to nest forms within the parent form.
		"""
		raise NotImplementedError('This method should be implemented by the subclass.')
	
	@classmethod
	def print_all(cls, formset_instance):
		print(formset_instance.management_form)
		for form in formset_instance.forms:
			print(form)
			if hasattr(form, 'nested_attr_name'):
				cls.print_all(getattr(form, form.nested_attr_name))
