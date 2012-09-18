from django.test.client import RequestFactory

from asymmetricbase.testing.base import BaseTestCase
from asymmetricbase.forms.formset_factoryfactory import FormSetFactoryFactory
from asymmetricbase import forms

class TestForm(forms.Form):
	field1 = forms.BooleanField(required = False)
	field2 = forms.IntegerField()

class FormsetFactoryFactoryTests(BaseTestCase):
	
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
