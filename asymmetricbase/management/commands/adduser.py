from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
	help = "adduser user group - adds a user to a group"
	
	def handle(self, *args, **options):
		if len(args) != 2:
			raise CommandError("Wrong number of arguments")
		
		username, groupname = args
		
		user = User.objects.get(username = username)
		group = Group.objects.get(name = groupname)
		
		user.groups.add(group)
