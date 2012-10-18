from django.forms.formsets import formset_factory, BaseFormSet

from asymmetricbase.logging import logger  # @UnusedImport
from asymmetricbase.forms.form_factory import FormFactory
from asymmetricbase.forms import ModelForm, make_modelformset_factory

class FormSetFactoryFactory(FormFactory):
	
	def __init__(self, form, *args, **kwargs):
		self.extra = kwargs.pop('extra', 0)
		self.max_num = kwargs.pop('max_num', 0)
		self.can_order = kwargs.pop('can_order', False)
		self.can_delete = kwargs.pop('can_delete', False)
		self.formset = kwargs.pop('formset', BaseFormSet)
		
		super(FormSetFactoryFactory, self).__init__(form, *args, **kwargs)
	
	def __call__(self, request):
		self.form = formset_factory(
			self.form,
			formset = self.formset, extra = self.extra,
			max_num = self.max_num, can_order = self.can_order,
			can_delete = self.can_delete
		)
		
		return super(FormSetFactoryFactory, self).__call__(request)

class ModelFormSetFactoryFactory(FormSetFactoryFactory):
	def __init__(self, model, form = ModelForm, *args, **kwargs):
		self.model = model
		super(ModelFormSetFactoryFactory, self).__init__(form, *args, **kwargs)
	
	def __call__(self, request):
		self.form = make_modelformset_factory(
			self.model, self.form,
			formset = self.formset, extra = self.extra,
			max_num = self.max_num, can_order = self.can_order,
			can_delete = self.can_delete
		)
		
		# Call the super of the super to bypass the super
		return super(FormSetFactoryFactory, self).__call__(request)
