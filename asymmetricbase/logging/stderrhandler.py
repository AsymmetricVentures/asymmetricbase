import logging
import sys
from pprint import pformat

class StdOutHandler(logging.Handler):
	def emit(self, record):
		sys.stderr.write(pformat(record.sql) + '\n')
