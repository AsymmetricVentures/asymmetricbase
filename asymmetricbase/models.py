from django.db import models
from django.utils import timezone

from asymmetricbase.logging import logger #@UnusedImport

class LogEntry(models.Model):
	date_created = models.DateTimeField(default = timezone.now)
	level = models.IntegerField()
	pathname = models.CharField(max_length = 255)
	lineno = models.IntegerField()
	msg = models.TextField(blank = True)
	args = models.TextField(blank = True)
	exc_info = models.TextField(blank = True)
	func = models.TextField(blank = True)
