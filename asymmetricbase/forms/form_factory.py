from copy import deepcopy

from django.http import QueryDict

from asymmetricbase.logging import logger #@UnusedImport
from asymmetricbase import forms

class FormFactory(object):
	
	def __init__(self, form, *args, **kwargs):
		self.form = form
		self.args = args
		self.data = {}
		
		self.callbacks = kwargs.pop('callbacks', [])
		self.init_callbacks = kwargs.pop('init_callbacks', [])
		
		# for inter-form dependencies
		self.children = set(kwargs.pop('children', []))
		self.parents = set(kwargs.pop('parents', []))
		self.use_GET = kwargs.pop('use_GET', False)
		
		self.kwargs = kwargs
		self.instance = None
		self.initial = {}
	
	def __call__(self, request):
		form_data = QueryDict('', mutable = True)
		form_data.update(self.data)
		if self.use_GET:
			form_data.update(request.GET)
		else:
			form_data.update(request.POST)
		
		if 'prefix' in self.kwargs:
			form_data = { k : v for k, v in form_data.items() if k.startswith(self.kwargs['prefix']) }
		
		self.args = (form_data or None,) + filter(lambda x: x is not None, self.args)
		
		if 'initial' in self.kwargs:
			self.kwargs['initial'].update(self.initial)
		else:
			self.kwargs['initial'] = self.initial

		if issubclass(self.form, forms.ModelForm) and 'instance' not in self.kwargs:
			self.kwargs['instance'] = self.instance
			
		if self.init_callbacks:
			class NewForm(self.form):
				def __init__(this, *args, **kwargs): #@NoSelf
					super(NewForm, this).__init__(*args, **kwargs)
					for callback in self.init_callbacks:
						callback(this)
			
			self.form = NewForm
		
		self.form_instance = self.form(*self.args, **self.kwargs)
		return self.form_instance
	
	def process_callbacks(self):
		for callback in self.callbacks:
			if callback is not None:
				callback(self.form_instance, self.form_instance.is_valid())
	
	def __deepcopy__(self, memo):
		form = deepcopy(self.form, memo)
		args = deepcopy(self.args, memo)
		callbacks = deepcopy(self.callbacks, memo)
		kwargs = deepcopy(self.kwargs, memo)
		kwargs['children'] = deepcopy(self.children, memo)
		kwargs['parents'] = deepcopy(self.parents, memo)
		kwargs['use_GET'] = self.use_GET
		return FormFactory(form, *args, callbacks = callbacks, **kwargs)