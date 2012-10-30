from django.forms.formsets import formset_factory, BaseFormSet

from asymmetricbase.logging import logger  # @UnusedImport
from asymmetricbase.forms.form_factory import FormFactory
from asymmetricbase.forms import ModelForm, make_modelformset_factory
from copy import deepcopy
from django.forms.models import BaseModelFormSet

class FormSetFactoryFactory(FormFactory):
	
	def __init__(self, form, *args, **kwargs):
		self.extra = kwargs.pop('extra', 0)
		self.max_num = kwargs.pop('max_num', 0)
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
		form = deepcopy(self.form, memo)
		args = deepcopy(self.args, memo)
		callbacks = deepcopy(self.callbacks, memo)
		kwargs = deepcopy(self.kwargs, memo)
		kwargs['children'] = deepcopy(self.children, memo)
		kwargs['parents'] = deepcopy(self.parents, memo)
		kwargs['use_GET'] = self.use_GET
		
		kwargs['extra'] = self.extra
		kwargs['max_num'] = self.max_num
		kwargs['can_order'] = self.can_order
		kwargs['can_delete'] = self.can_delete
		kwargs['formset'] = self.formset
		
		return FormSetFactoryFactory(form, *args, callbacks = callbacks, **kwargs)

class ModelFormSetFactoryFactory(FormSetFactoryFactory):
	def __init__(self, model, form = ModelForm, *args, **kwargs):
		self.model = model
		# use BaseModelFormSet if none is given (since super defaults to BaseFormSet
		kwargs.setdefault('formset', BaseModelFormSet)
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
	
	def __deepcopy__(self, memo):
		# FormFactory deepcopy returns a FormFactory object, so deepcopy
		# needs to be overridden to return this class
		# TODO It would be nice to refactor this so that all the kwargs copying
		# isn't repeated here and in FormSetFactoryFactory, but the extra model
		# argument makes it difficult
		model = deepcopy(self.model, memo)
		form = deepcopy(self.form, memo)
		args = deepcopy(self.args, memo)
		callbacks = deepcopy(self.callbacks, memo)
		kwargs = deepcopy(self.kwargs, memo)
		kwargs['children'] = deepcopy(self.children, memo)
		kwargs['parents'] = deepcopy(self.parents, memo)
		kwargs['use_GET'] = self.use_GET
		
		kwargs['extra'] = self.extra
		kwargs['max_num'] = self.max_num
		kwargs['can_order'] = self.can_order
		kwargs['can_delete'] = self.can_delete
		kwargs['formset'] = self.formset
		
		return ModelFormSetFactoryFactory(model, form, *args, callbacks = callbacks, **kwargs)