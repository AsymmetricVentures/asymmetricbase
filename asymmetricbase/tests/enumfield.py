from django.test.client import RequestFactory

from asymmetricbase.testing.base_with_models import BaseTestCaseWithModels
from asymmetricbase.tests.models import TestEnum, TestEnumModel, TestEnumModelWithDefault
from asymmetricbase import forms

class TestForm(forms.Form):
	pass

class TestModelForm(forms.ModelForm):
	class Meta(object):
		model = TestEnumModel
		fields = ('field1',)

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
	
	def test_get_default(self):
		model = TestEnumModelWithDefault()
		model.save()
