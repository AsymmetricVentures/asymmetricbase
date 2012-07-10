from asymmetricbase.logging import logger, line_logger

class TraceLogger(object):
	
	def _flush(self):
		for handler in logger.handlers:
			if hasattr(handler, 'flush'):
				handler.flush()
	
	def process_request(self, request):
		return None
	
	def process_response(self, request, response):
		self._flush()
		return response
	
	def process_exception(self, request, exception):
		self._flush()
		line_logger.exception('Got exception: {}'.format(exception))
		return None
