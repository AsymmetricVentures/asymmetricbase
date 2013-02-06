import imp

from django.core.management.base import BaseCommand, CommandError
from django.core.urlresolvers import RegexURLResolver
from django.utils.importlib import import_module
from django.contrib.auth.models import Permission

from asymmetricbase.utils.permissions import default_content_type, create_codename
from asymmetricbase.views.base import AsymBaseView

class Command(BaseCommand):
	args = '<urls.py file>'
	
	objs = []
	codenames = set()
	names = {}
	
	def handle(self, *args, **options):
		
		self.verbose = options.get('verbosity', 0)
		
		if len(args) == 0:
			raise CommandError("Command requires one argument")
		
		urls_path = args[0]
		
		try:
			urls = imp.load_source('urls', urls_path)
		except (ImportError, IOError):
			raise CommandError("Could not import file {}".format(urls_path))
		
		# all view permissions will be assigned to User content type
		self.ctype = default_content_type()
		# get existing permissions
		self.db_perms = Permission.objects.filter(content_type = self.ctype).values_list('codename')
		
		# traverse defined url patterns to get all views
		self.traverse(urls.urlpatterns)
		
		# insert permissions into DB
		Permission.objects.bulk_create(self.objs)
	
	def traverse(self, patterns):
		for entry in patterns:
			if isinstance(entry, RegexURLResolver):
				for k, v in entry.reverse_dict.items():
					# class-based views are called through .as_view(), so they'll be
					# callable here
					if callable(k):
						kwargs = v[2]
						cls = getattr(import_module(k.__module__), k.func_name)
						
						if hasattr(cls, 'permission_name') and getattr(cls, 'login_required', None):
							msg = ''
							suffix = ''
							# if name is not given, use default name from class name:
							if getattr(cls, 'permission_name') is '':
								name = 'Can Access {}'.format(cls.__name__)
								msg = 'Default: Default'
							else:
								name = getattr(cls, 'permission_name')
								msg = 'Add: Named'
								
								# For view classes that are used in more than one
								# view but are distinguished by kwargs, we can create
								# separate permissions by requiring that the view's
								# permission_name attribute be a dictionary in the following format:
								# permission_name[kwarg_key][kwarg_value] = { permission_name : '<name>', permission_codename : '<codename>' }
								if isinstance(name, dict):
									name, suffix = AsymBaseView.get_view_name_and_suffix(name, **kwargs)
										
								
							codename = create_codename(k.__module__, cls.__name__, suffix)
							
							# check for name conflicts
							if name in self.names and codename != self.names[name] and self.verbose:
								print 'Duplicate: Permission at {} with name \'{}\' already defined at {}.'.format(codename, name, self.names[name])
							# check that permission is not already defined for this class
							if (codename,) not in self.db_perms:
								if codename not in self.codenames:
									self.codenames.add(codename)
									self.objs.append(
										Permission(
											name = name,
											codename = codename,
											content_type = self.ctype,
										)
									)
								if self.verbose:
									print '{} Permission: {} at {}.'.format(msg, name, codename)
							else:
								perm = Permission.objects.get(content_type = self.ctype, codename = codename)
								perm.name = name
								perm.save()
								if self.verbose:
									print 'Update: Permission \'{}\' updated at {}.'.format(name, codename)
							
							self.names[name] = codename
						elif getattr(cls, 'login_required', True) is False and self.verbose:
							print 'Skip: Login not required for {}.{} so permission not added.'.format(k.__module__, cls.__name__)
						elif self.verbose:
							print 'Warning: permission_name not defined on {}.{}.'.format(k.__module__, cls.__name__)
						
			if hasattr(entry, 'url_patterns'):
				self.traverse(entry.url_patterns)
