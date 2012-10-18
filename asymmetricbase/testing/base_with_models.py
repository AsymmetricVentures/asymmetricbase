from django.core.management import call_command
from django.db.models import loading
from django.conf import settings

from asymmetricbase.testing.base import BaseTestCase

class BaseTestCaseWithModels(BaseTestCase):
	
	def _pre_setup(self):
		loading.cache.loaded = False
		self._original_installed_apps = list(settings.INSTALLED_APPS)
		settings.INSTALLED_APPS = self._original_installed_apps + ['asymmetricbase.tests', ]
		
		call_command('syncdb', interactive = False, verbosity = 0, migrate = False)
		
		super(BaseTestCaseWithModels, self)._pre_setup()
	
	def _post_teardown(self):
		super(BaseTestCaseWithModels, self)._post_teardown()
		# restore settings
		settings.INSTALLED_APPS = self._original_installed_apps
		loading.cache.loaded = False
