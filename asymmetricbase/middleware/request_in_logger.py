from asymmetricbase.logging import logger, audit_logger


class AddRequestToLoggerMiddleware(object):
	''' Adds the request object to all the loggers.
	This removes the need to store it in a thread global to access it in the
	logging classes'''
	
	def process_request(self, request):
		for l in (logger, audit_logger):
			for handler in l.handlers:
				setattr(handler, 'django_request', request)
