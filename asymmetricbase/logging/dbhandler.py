import logging
from datetime import datetime

from django.utils.timezone import utc

class DBLoggingHandler(logging.Handler):
	
	def emit(self, record):
		log_generator = DBLogGenerator(record)
		log_generator.generate()

class DBLogGenerator(object):
	def __init__(self, record):
		self.record = record
	
	def generate(self):
		
		self._save_log_entry()
	
	def _save_log_entry(self):
		
		from django.db import transaction
		from asymmetricbase.models import LogEntry
		
		with transaction.commit_on_success():
			LogEntry.objects.create(
				date_created = datetime.fromtimestamp(self.record.created, utc),
				level = self.record.levelno,
				pathname = str(self.record.pathname),
				lineno = self.record.lineno,
				msg = repr(self.record.msg),
				args = repr(self.record.args),
				exc_info = repr(self.record.exc_info),
				func = repr(self.record.funcName)
			)
