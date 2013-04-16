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
from django.forms.formsets import formset_factory

from asymmetricbase.testing.base_with_models import BaseTestCaseWithModels
from asymmetricbase.tests.models import TestEnum, TestEnumModel, TestEnumModelWithDefault, TestEnumModel1
from asymmetricbase import forms
from asymmetricbase.fields.enumfield import EnumField

class TestForm(forms.Form):
	field1 = EnumField(TestEnum).formfield(required = True)
	field2 = EnumField(TestEnum, default = TestEnum.VALUE2).formfield()

class TestModelForm(forms.ModelForm):
	class Meta(object):
		model = TestEnumModel
		fields = ('field1',)

class TestModelWithDefaultForm(forms.ModelForm):
	class Meta(object):
		model = TestEnumModelWithDefault
		fields = ('field1',)

#class TestOldEnumForm(forms.ModelForm):
#	class Meta(object):
#		model = TestOldEnumModelWithDefault

TestModelFormSet = forms.make_modelformset_factory(TestEnumModel1)
TestFormSet = formset_factory(TestForm)

class EnumFieldTests(BaseTestCaseWithModels):
	
	def setUp(self):
		self.factory = RequestFactory()
	
	
	def test_validation1(self):
		request = self.factory.post('/', {
			'field1' : '1'
		})
		
		form = TestModelForm(request.POST)
		self.assertTrue(form.is_valid())
		
		model = form.save()
		self.assertEqual(model.field1, TestEnum.VALUE1)
	
	def test_validation2(self):
		request = self.factory.post('/', {
			'field1' : '8'
		})
		
		form = TestModelForm(request.POST)
		self.assertFalse(form.is_valid())
		
	def test_querying1(self):
		TestEnumModel.objects.bulk_create([
			TestEnumModel(field1 = TestEnum.VALUE1),
			TestEnumModel(field1 = TestEnum.VALUE2),
			TestEnumModel(field1 = TestEnum.VALUE1),
			TestEnumModel(field1 = TestEnum.VALUE2),
			TestEnumModel(field1 = TestEnum.VALUE1),
		])
		
		self.assertEqual(TestEnumModel.objects.filter(field1 = TestEnum.VALUE1).count(), 3)
		self.assertEqual(TestEnumModel.objects.filter(field1 = '1').count(), 3)
		
	def test_querying2(self):
		TestEnumModel.objects.bulk_create([
			TestEnumModel(field1 = TestEnum.VALUE1),
			TestEnumModel(field1 = TestEnum.VALUE2),
			TestEnumModel(field1 = TestEnum.VALUE1),
			TestEnumModel(field1 = TestEnum.VALUE2),
			TestEnumModel(field1 = TestEnum.VALUE1),
		])
		
		v1 = TestEnumModel.objects.filter(field1 = '1')
		
		self.assertEqual(v1[0].field1, TestEnum.VALUE1)
		self.assertNotEqual(v1[0].field1, 1)
	
	def test_widget_selected(self):
		model = TestEnumModel()
		model.field1 = TestEnum.VALUE2
		
		form = TestModelForm(instance = model)
		
		substring_html = '<option value="{}" selected="selected">{}</option>'.format(int(TestEnum.VALUE2), str(TestEnum.VALUE2))
		
		self.assertHTMLContains(form, substring_html)
	
	def test_widget_with_initial(self):
		form = TestModelWithDefaultForm()
		
		substring_html = '<option value="{}" selected="selected">{}</option>'.format(int(TestEnum.VALUE1), str(TestEnum.VALUE1))
		
		self.assertHTMLContains(unicode(form), substring_html)
		
	def test_get_default(self):
		model = TestEnumModelWithDefault()
		model.save()
		
		self.assertEqual(model.field1, TestEnum.VALUE1)
		
	def test_with_formset1(self):
		request = self.factory.post('/', {
			'form-TOTAL_FORMS' : '1',
			'form-INITIAL_FORMS' : '0',
			'form-MAX_NUM_FORMS' : '0',
			'form-0-field1' : '',
			'form-0-field2' : '2',
		})
		
		formset = TestFormSet(request.POST)
		
		self.assertFalse(formset[0].has_changed())
		self.assertFalse(formset.has_changed())
		self.assertTrue(formset.is_valid())
