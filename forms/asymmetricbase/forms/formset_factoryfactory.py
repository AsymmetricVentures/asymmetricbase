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
from copy import deepcopy

from django.forms.formsets import formset_factory, BaseFormSet
from django.forms.models import BaseModelFormSet, BaseInlineFormSet

from asymmetricbase.logging import logger # @UnusedImport

from . import ModelForm, make_modelformset_factory, make_inlineformset_factory
from .form_factory import FormFactory

class AsymFormFactoryFactoryDeepcopier(object):
	form = None
	args = None
	callbacks = None
	kwargs = None
	
	def do_deepcopy(self, instance, memo):
		self.form = deepcopy(instance.form, memo)
		self.args = deepcopy(instance.args, memo)
		self.callbacks = deepcopy(instance.callbacks, memo)
		self.kwargs = deepcopy(instance.kwargs, memo)
		self.kwargs['children'] = deepcopy(instance.children, memo)
		self.kwargs['parents'] = deepcopy(instance.parents, memo)
		self.kwargs['use_GET'] = instance.use_GET
		self.kwargs['use_REQUEST'] = instance.use_REQUEST
		self.kwargs['always_bound'] = instance.always_bound
		
		self.kwargs['extra'] = instance.extra
		self.kwargs['max_num'] = instance.max_num
		self.kwargs['can_order'] = instance.can_order
		self.kwargs['can_delete'] = instance.can_delete
		self.kwargs['formset'] = instance.formset

class FormSetFactoryFactory(FormFactory):
	
	def __init__(self, form, *args, **kwargs):
		self.extra = kwargs.pop('extra', 0)
		self.max_num = kwargs.pop('max_num', None)
		self.can_order = kwargs.pop('can_order', False)
		self.can_delete = kwargs.pop('can_delete', False)
		self.formset = kwargs.pop('formset', BaseFormSet)
		
		super(FormSetFactoryFactory, self).__init__(form, *args, **kwargs)
		
		# formsets have lists of dictionaries as initial
		self.initial = []
	
	def __call__(self, request):
		self.form = formset_factory(
			self.form,
			formset = self.formset, extra = self.extra,
			max_num = self.max_num, can_order = self.can_order,
			can_delete = self.can_delete
		)
		
		return super(FormSetFactoryFactory, self).__call__(request)
	
	def __deepcopy__(self, memo):
		# FormFactory deepcopy returns a FormFactory object, so deepcopy
		# needs to be overridden to return this class
		copier = AsymFormFactoryFactoryDeepcopier()
		copier.do_deepcopy(self, memo)
		
		return FormSetFactoryFactory(copier.form, *copier.args, callbacks = copier.callbacks, **copier.kwargs)

class ModelFormSetFactoryFactory(FormSetFactoryFactory):
	def __init__(self, model, form = ModelForm, *args, **kwargs):
		self.model = model
		self.formargs = kwargs.pop('formargs', {})
		# use BaseModelFormSet if none is given (since super defaults to BaseFormSet
		kwargs.setdefault('formset', BaseModelFormSet)
		super(ModelFormSetFactoryFactory, self).__init__(form, *args, **kwargs)
	
	def __call__(self, request):
		self.form = make_modelformset_factory(
			self.model, self.form,
			formset = self.formset, extra = self.extra,
			max_num = self.max_num, can_order = self.can_order,
			can_delete = self.can_delete,
			formargs = self.formargs,
		)
		
		# Call the super of the super to bypass the super
		return super(FormSetFactoryFactory, self).__call__(request)
	
	def __deepcopy__(self, memo):
		# FormFactory deepcopy returns a FormFactory object, so deepcopy
		# needs to be overridden to return this class
		model = deepcopy(self.model, memo)
		copier = AsymFormFactoryFactoryDeepcopier()
		copier.do_deepcopy(self, memo)
		
		return ModelFormSetFactoryFactory(model, copier.form, *copier.args, callbacks = copier.callbacks, **copier.kwargs)

class InlineFormSetFactoryFactory(FormSetFactoryFactory):
	def __init__(self, parent_model, model, form = ModelForm, fk_name = None, *args, **kwargs):
		self.parent_model = parent_model
		self.model = model
		self.fk_name = fk_name
		self.formargs = kwargs.pop('formargs', {})
		# use BaseInlineFormSet if none is given (since super defaults to BaseFormSet
		kwargs.setdefault('formset', BaseInlineFormSet)
		super(InlineFormSetFactoryFactory, self).__init__(form, *args, **kwargs)
	
	def __call__(self, request):
		self.form = make_inlineformset_factory(
			self.parent_model,
			self.model,
			self.form,
			formset = self.formset,
			fk_name = self.fk_name,
			extra = self.extra,
			max_num = self.max_num,
			can_order = self.can_order,
			can_delete = self.can_delete,
			formargs = self.formargs,
		)
		
		# Call the super of the super to bypass the super
		return super(FormSetFactoryFactory, self).__call__(request)
	
	def __deepcopy__(self, memo):
		# FormFactory deepcopy returns a FormFactory object, so deepcopy
		# needs to be overridden to return this class
		model = deepcopy(self.model, memo)
		copier = AsymFormFactoryFactoryDeepcopier()
		copier.do_deepcopy(self, memo)
		
		return InlineFormSetFactoryFactory(model, copier.form, *copier.args, callbacks = copier.callbacks, **copier.kwargs)
