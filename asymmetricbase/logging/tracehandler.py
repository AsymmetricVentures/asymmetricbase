import logging
from logging import CRITICAL, DEBUG, ERROR, FATAL, INFO, WARN

class DBTraceHandler(logging.Handler):
	def __init__(self):
		self.rows = []
		self.django_request = None
		super(DBTraceHandler, self).__init__()
	
	def emit(self, record):
		if self.django_request is None:
			return
		self.rows.append(DBTraceLogGenerator(self.django_request, record).generate())
	
	def flush(self):
		from django.db import connection
		from django.db.utils import DatabaseError
		from asymmetricbase.models import TraceEntry
		entry = TraceEntry(get = getattr(self.django_request, 'path', ''))
		msg = ''
		
		for row in self.rows:
			msg_row = '''[{level}] {file_name}:{lineno} {msg}\n'''
			
			if row['exc_info']:
				entry.exc_info = row['exc_info']
			
			msg += msg_row.format(**row)
		
		if len(msg) > 1:
			entry.msg = msg
			try:
				# "current transaction is aborted, commands ignored until end of transaction block"
				# If there is a database error before this point, then this
				# insert may fail because we may still be inside a transaction
				# block. So, we rollback and allow the code to continue. 
				entry.save()
			except DatabaseError:
				connection._rollback()
		self.rows = []
		
class DBTraceLogGenerator(object):
	def __init__(self, request, record):
		self.request = request
		self.record = record
	
	def generate(self):
		return {
			'file_name' : self.record.pathname,
			'lineno' : self.record.lineno,
			'level' : {CRITICAL : 'C', DEBUG : 'D', ERROR : 'E', FATAL : 'F', INFO : 'I', WARN : 'W'}.get(self.record.levelno, 'I'),
			'msg' : self.record.msg,
			'exc_info' : self.record.exc_info,
		}
