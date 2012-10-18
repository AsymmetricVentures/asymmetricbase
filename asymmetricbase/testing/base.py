from django.test import TestCase
from django.conf import settings

from asymmetricbase.views.mixins.merge_attr import MergeAttrMixin
from asymmetricbase.testing.model_initializer import install_initializers

class BaseTestCase(TestCase, MergeAttrMixin):
	"""Base class for all tests"""
	pre_initalizers = []
	
	def __init__(self, *args, **kwargs):
		super(BaseTestCase, self).__init__(*args, **kwargs)
		settings.IS_IN_TEST = True
	
	def __del__(self):
		"Hook method for deconstructing the class fixture after running all tests in the class."
		settings.IS_IN_TEST = False
	
	def _fixture_setup(self):
		super(BaseTestCase, self)._fixture_setup()
		
		all_initializers = self.pre_initalizers + self._get_inherited_initializers()
		
		self.initialized_instances = install_initializers(all_initializers)
	
	def _fixture_teardown(self):
		super(BaseTestCase, self)._fixture_teardown()
		for mi in self.initialized_instances:
			mi.finalize()
		self.initialized_instances = []
	
	def _get_inherited_initializers(self):
		"Returns a list of all initializers defined in this class and all its parents"
		return self._merge_attr('initializers').keys()
		# TODO: check if this is equivalent to _merge_attr
# 		initializers = []
# 		curr_class = self.__class__
# 		while(issubclass(curr_class, BaseTestCase)):
# 			new_initializers = [
# 				initializer for initializer in getattr(curr_class, 'initializers', [])
# 				if initializer not in initializers
# 			]
# 			initializers = new_initializers + initializers
# 			curr_class = curr_class.__bases__[0]
# 		return initializers
