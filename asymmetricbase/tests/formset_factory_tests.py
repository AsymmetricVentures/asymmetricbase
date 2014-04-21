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

from django.test.client import RequestFactory
from django.forms.models import BaseInlineFormSet

from asymmetricbase.testing.base_with_models import BaseTestCaseWithModels
from asymmetricbase.forms.formset_factoryfactory import FormSetFactoryFactory, \
	ModelFormSetFactoryFactory, InlineFormSetFactoryFactory
from asymmetricbase.forms.nested_formset import BaseNestedFormSet
from asymmetricbase import forms
from asymmetricbase.tests.models import TestModel, FKTestModel, FKFKTestModel

class TestForm(forms.Form):
	field1 = forms.BooleanField(required = False)
	field2 = forms.IntegerField()

class TestModelForm(forms.ModelForm):
	class Meta(object):
		model = TestModel

class TestInlineForm(forms.ModelForm):
	class Meta(object):
		model = FKTestModel

class TestNestedInlineFormSet(BaseInlineFormSet, BaseNestedFormSet):
	"""
	InlineFormSets can be nested by overriding the
	add_fields method and saving subforms as an attribute
	on the form.
	stackoverflow.com/questions/7648368/django-inline-formset-setup
	"""
	
	def _generate_formset(self, request, instance, pk_value):
		return InlineFormSetFactoryFactory(
			FKTestModel,
			FKFKTestModel,
			extra = 1,
			max_num = None,
			instance = instance,
			prefix = 'FKFK_FORMSET_%s' % pk_value,
		)

class FormsetFactoryFactoryTests(BaseTestCaseWithModels):
	
	def setUp(self):
		self.factory = RequestFactory()
	
	def test_create_formset1(self):
		request = self.factory.post('/', {
			'form-TOTAL_FORMS' : '2',
			'form-INITIAL_FORMS' : '0',
			'form-MAX_NUM_FORMS' : '',
			'form-0-field1' : '1',
			'form-0-field2' : '2',
			'form-1-field1' : 'False',
			'form-1-field2' : '4',
		},)
		
		form_instance = FormSetFactoryFactory(TestForm)(request)
		self.assertTrue(form_instance.is_valid())
		
		form1 = form_instance[0]
		form2 = form_instance[1]
		
		self.assertEqual(form1.cleaned_data['field1'], True)
		self.assertEqual(form1.cleaned_data['field2'], 2)
		
		self.assertEqual(form2.cleaned_data['field1'], False)
		self.assertEqual(form2.cleaned_data['field2'], 4)
	
	def test_create_modelformset1(self):
		request = self.factory.post('/', {
			'form-TOTAL_FORMS' : '2',
			'form-INITIAL_FORMS' : '0',
			'form-MAX_NUM_FORMS' : '',
			'form-0-field1' : '1',
			'form-0-field2' : 'Hello',
			'form-1-field1' : '4',
			'form-1-field2' : 'World',
		})
		
		form_instance = ModelFormSetFactoryFactory(TestModel, TestModelForm, extra = 0)(request)
		self.assertTrue(form_instance.is_valid())
		
		form1 = form_instance[0]
		form2 = form_instance[1]
		
		self.assertEqual(form1.cleaned_data['field1'], 1)
		self.assertEqual(form1.cleaned_data['field2'], 'Hello')
		
		self.assertEqual(form2.cleaned_data['field1'], 4)
		self.assertEqual(form2.cleaned_data['field2'], 'World')
	
	def test_instantiate_inlineformset1(self):
		"""
		Just make sure there are no exceptions.
		"""
		# create top level TestModel
		test_model = TestModel.objects.create(field1 = True, field2 = 1)
		# create two FKTestModel instances with ForeignKey to test_model
		fk_test_model1 = FKTestModel.objects.create( #@UnusedVariable
			test_model = test_model,
			field1 = True,
			field2 = 1,
		)
		fk_test_model2 = FKTestModel.objects.create( #@UnusedVariable
			test_model = test_model,
			field1 = True,
			field2 = 1,
		)
		request = self.factory.get('/')
		form_instance = InlineFormSetFactoryFactory(TestModel, FKTestModel, instance = test_model, extra = 0)(request) #@UnusedVariable
	
	def test_create_inlineformset1(self):
		# create top level TestModel
		test_model = TestModel.objects.create(field1 = True, field2 = 1)
		request = self.factory.post('/', {
			'fktestmodel_set-TOTAL_FORMS' : '2',
			'fktestmodel_set-INITIAL_FORMS' : '0',
			'fktestmodel_set-MAX_NUM_FORMS' : '',
			'fktestmodel_set-0-test_model' : test_model.id,
			'fktestmodel_set-0-field1' : '1',
			'fktestmodel_set-0-field2' : 'Hello',
			'fktestmodel_set-1-test_model' : test_model.id,
			'fktestmodel_set-1-field1' : '4',
			'fktestmodel_set-1-field2' : 'World',
		})
		form_instance = InlineFormSetFactoryFactory(TestModel, FKTestModel, instance = test_model, extra = 0)(request)
		
		self.assertTrue(form_instance.is_valid())
		
		form1 = form_instance[0]
		form2 = form_instance[1]
		
		self.assertEqual(form1.cleaned_data['test_model'], test_model)
		self.assertEqual(form1.cleaned_data['field1'], 1)
		self.assertEqual(form1.cleaned_data['field2'], 'Hello')
		
		self.assertEqual(form2.cleaned_data['test_model'], test_model)
		self.assertEqual(form2.cleaned_data['field1'], 4)
		self.assertEqual(form2.cleaned_data['field2'], 'World')
		
	def test_get_nested_inlineformset(self):
		# create top level TestModel
		test_model = TestModel.objects.create(field1 = True, field2 = 1)
		# create two FKTestModel instances with ForeignKey to test_model
		fk_test_model1 = FKTestModel.objects.create(
			test_model = test_model,
			field1 = True,
			field2 = 1,
		)
		fk_test_model2 = FKTestModel.objects.create(
			test_model = test_model,
			field1 = True,
			field2 = 1,
		)
		# for each of these, create two FKFKTestModel instances
		fk_fk_test_model1 = FKFKTestModel.objects.create( #@UnusedVariable
			fk_test_model = fk_test_model1,
			field1 = True,
			field2 = 1,
		)
		fk_fk_test_model2 = FKFKTestModel.objects.create( #@UnusedVariable
			fk_test_model = fk_test_model1,
			field1 = True,
			field2 = 1,
		)
		fk_fk_test_model3 = FKFKTestModel.objects.create( #@UnusedVariable
			fk_test_model = fk_test_model2,
			field1 = True,
			field2 = 1,
		)
		fk_fk_test_model4 = FKFKTestModel.objects.create( #@UnusedVariable
			fk_test_model = fk_test_model2,
			field1 = True,
			field2 = 1,
		)
		request = self.factory.get('/')
		factory = InlineFormSetFactoryFactory(
			TestModel,
			FKTestModel,
			formset = TestNestedInlineFormSet,
			instance = test_model,
			extra = 0,
			max_num = None,
			request = request,
		)
		form_instance = factory(request) #@UnusedVariable
		
#		TestNestedInlineFormSet.print_all(form_instance)
	
	def test_post_nested_inlineformset(self):
		# create top level TestModel
		test_model = TestModel.objects.create(field1 = True, field2 = 1)
		# create a FKTestModel instance with ForeignKey to test_model
		fk_test_model1 = FKTestModel.objects.create(
			test_model = test_model,
			field1 = True,
			field2 = 1,
		)
		request = self.factory.post('/', {
			'fktestmodel_set-TOTAL_FORMS' : '1',
			'fktestmodel_set-INITIAL_FORMS' : '1',
			'fktestmodel_set-MAX_NUM_FORMS' : '',
			'fktestmodel_set-0-test_model' : test_model.id,
			'fktestmodel_set-0-field1' : 1,
			'fktestmodel_set-0-field2' : 1,
			'fktestmodel_set-0-id' : test_model.id,
			'FKFK_FORMSET_1-TOTAL_FORMS' : '1',
			'FKFK_FORMSET_1-INITIAL_FORMS' : '0',
			'FKFK_FORMSET_1-0-fk_test_model' : fk_test_model1.id,
			'FKFK_FORMSET_1-0-field1' : 1,
			'FKFK_FORMSET_1-0-field2' : 1,
		})
		factory = InlineFormSetFactoryFactory(
			TestModel,
			FKTestModel,
			formset = TestNestedInlineFormSet,
			instance = test_model,
			extra = 0,
			max_num = None,
			request = request,
		)
		
		form_instance = factory(request)
		
#		TestNestedInlineFormSet.print_all(form_instance)
		
		self.assertTrue(form_instance.is_valid())
		
		form1 = form_instance[0]
		
		self.assertEqual(form1.cleaned_data['test_model'], test_model)
		self.assertEqual(form1.cleaned_data['field1'], 1)
		self.assertEqual(form1.cleaned_data['field2'], '1')
		
		for form in form1.nested:
			self.assertTrue(form.is_valid())
