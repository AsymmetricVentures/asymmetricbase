import logging

from logging import CRITICAL, DEBUG, ERROR, FATAL, INFO, WARN

class DBTraceHandler(logging.Handler):
	def __init__(self):
		self.rows = []
		self.django_request = None
		super(DBTraceHandler, self).__init__()
	
	def emit(self, record):
		self.rows.append(DBTraceLogGenerator(self.django_request, record).generate())
	
	def flush(self):
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
			entry.save()
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
