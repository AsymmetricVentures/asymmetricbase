from django.test.client import RequestFactory

from asymmetricbase.testing.base_with_models import BaseTestCaseWithModels
from asymmetricbase.forms.formset_factoryfactory import FormSetFactoryFactory, \
	ModelFormSetFactoryFactory, InlineFormSetFactoryFactory
from asymmetricbase import forms
from asymmetricbase.tests.models import TestModel, FKTestModel, FKFKTestModel
from django.forms.models import BaseInlineFormSet

class TestForm(forms.Form):
	field1 = forms.BooleanField(required = False)
	field2 = forms.IntegerField()

class TestModelForm(forms.ModelForm):
	class Meta(object):
		model = TestModel

class TestInlineForm(forms.ModelForm):
	class Meta(object):
		model = FKTestModel

class TestNestedInlineFormSet(BaseInlineFormSet):
	"""
	InlineFormSets can be nested by overriding the
	add_fields method and saving subforms as an attribute
	on the form.
	stackoverflow.com/questions/7648368/django-inline-formset-setup
	"""
	def add_fields(self, form, index):
		# allow the superclass to add fields as usual
		super(TestNestedInlineFormSet, self).add_fields(form, index)
		
		try:
			instance = self.get_queryset()[index]
			pk_value = instance.pk
		except IndexError:
			instance = None
			pk_value = hash(form.prefix)
		
		# define a formset
		FKFKTestFormset = InlineFormSetFactoryFactory(
			FKTestModel,
			FKFKTestModel,
			extra = 0,
			instance = instance,
			prefix = 'FKFK_FORMSET_%s' % pk_value,
		)
		# store the formset on the form
		class dummy_request(object):
			GET = {}
			POST = {}
		
		form.nested = [FKFKTestFormset(dummy_request())]
		

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
		
	def test_create_nested_inlineformset(self):
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
		fk_fk_test_model1 = FKFKTestModel.objects.create(
			fk_test_model = fk_test_model1,
			field1 = True,
			field2 = 1,
		)
		fk_fk_test_model2 = FKFKTestModel.objects.create(
			fk_test_model = fk_test_model1,
			field1 = True,
			field2 = 1,
		)
		fk_fk_test_model3 = FKFKTestModel.objects.create(
			fk_test_model = fk_test_model2,
			field1 = True,
			field2 = 1,
		)
		fk_fk_test_model4 = FKFKTestModel.objects.create(
			fk_test_model = fk_test_model2,
			field1 = True,
			field2 = 1,
		)
#		request = self.factory.post('/', {
#			'form-TOTAL_FORMS' : '2',
#			'form-INITIAL_FORMS' : '0',
#			'form-MAX_NUM_FORMS' : '',
#			'form-0-field1' : '1',
#			'form-0-field2' : 'Hello',
#			'form-1-field1' : '4',
#			'form-1-field2' : 'World',
#		})
		request = self.factory.get('/')
		form_instance = InlineFormSetFactoryFactory(
			TestModel,
			FKTestModel,
			formset = TestNestedInlineFormSet,
			instance = test_model,
			extra = 0
		)(request)
		
		self.assertTrue(form_instance.is_valid())
