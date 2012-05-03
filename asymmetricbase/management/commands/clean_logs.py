from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

class Command(BaseCommand):
	
	def handle(self, *args, **options):
		from asymmetricbase.models import LogEntry
		
		cutoff = timezone.now() - timedelta(days = getattr(settings, 'ASYM_KEEP_LOGS',  4)) # only keep 4 days worth
		
		LogEntry.objects.filter(
			date_created__lt = cutoff
		).delete()
