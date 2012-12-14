import unittest

from asymmetricbase.utils.cached_function import cached_function

class TestCachedFunction(unittest.TestCase):
	
	def test_cached_function(self):
		self.outer_var = 100
		
		@cached_function
		def method_to_test():
			self.outer_var += 1
			return 42
		
		self.assertEqual(method_to_test(), 42)
		self.assertEqual(self.outer_var, 101)
		self.assertEqual(method_to_test(), 42)
		self.assertEqual(self.outer_var, 101)
