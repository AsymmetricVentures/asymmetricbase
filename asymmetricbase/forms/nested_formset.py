from django.forms.models import BaseModelFormSet

class BaseNestedFormSet(BaseModelFormSet):
	
	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request')
		assert(self.request is not None)
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
		nested_formset_factory_factory = self._generate_formset(instance, pk_value)
		
		form.nested = [nested_formset_factory_factory(self.request)]
	
	def _generate_formset(self, instance, pk_value):
		"""
		Returns an instance of FormSetFactoryFactory
		(or ModelFormSetFactoryFactory, or InlineFormSetFactoryFactory)
		that should be used to nest forms within the parent form.
		"""
		raise NotImplementedError('This method should be implemented by the subclass.')
	
	@classmethod
	def print_all(cls, form_instance):
		print form_instance.management_form
		for form in form_instance.forms:
			print form
			if hasattr(form, 'nested'):
				for f in form.nested:
					cls.print_all(f)