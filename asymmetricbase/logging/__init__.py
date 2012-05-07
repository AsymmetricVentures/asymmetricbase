import logging
from django.conf import settings

class NullHandler(logging.Handler):
	def emit(self, record):
		pass

def init_logger():
	logger_name = getattr(settings, 'ASYM_LOGGER', 'asymm_logger')
	
	_logger = logging.getLogger(logger_name)
	logger.addHandler(NullHandler())
	return _logger

logger = init_logger()
