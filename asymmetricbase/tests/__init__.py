from asymmetricbase.testing.build_test_suite_form import build_test_suite_from

from formset_factory_tests import FormsetFactoryFactoryTests
from enumfield import EnumFieldTests
from cached_function import TestCachedFunction

def suite():
	return build_test_suite_from((
		FormsetFactoryFactoryTests,
		EnumFieldTests,
		TestCachedFunction
	))
