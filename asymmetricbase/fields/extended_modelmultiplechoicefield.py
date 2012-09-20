from asymmetricbase import forms

class ExtendedModelMultipleChoiceField(forms.ModelMultipleChoiceField):
	''' Works the same as a ModelMultipleChoiceField except that it works
		in tandom with fielditerator to provide the model instance that the
		choice is representing
	'''
	
	def prepare_value(self, value):
		if hasattr(value, '_meta'):
			return (value, super(ExtendedModelMultipleChoiceField, self).prepare_value(value))
		return super(ExtendedModelMultipleChoiceField, self).prepare_value(value)
