import pytz

from django.utils import timezone
from django.conf import settings

class TimezoneMiddleware(object):
	""" Set the timezone on each request to the default one """
	def process_request(self, request):
		timezone.activate(pytz.timezone(settings.TIME_ZONE))
