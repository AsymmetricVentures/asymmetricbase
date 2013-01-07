from django.contrib.contenttypes.models import ContentType
from asymmetricbase.utils.cached_function import cached_function

@cached_function
def default_content_type():
	return ContentType.objects.get(model = 'user')

def default_content_type_appname():
	return 'auth'

def create_codename(module_path, cls_name, suffix = ''):
	# Remove the repeated parts of the path
	module_path = module_path.replace('.views', '').replace('project.', '')
	
	# return only the first 100 characters, since that's
	# all that fits in the DB
	return 'view_{}.{}{}'.format(
		module_path,
		cls_name,
		suffix
	)[:100]
