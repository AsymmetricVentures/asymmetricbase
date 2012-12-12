from django.contrib.contenttypes.models import ContentType

def default_content_type():
	return ContentType.objects.get(model = 'user')

def default_content_type_appname():
	return 'auth'

def create_codename(module_path, cls_name):
	# return only the first 100 characters, since that's
	# all that fits in the DB
	return 'view_{}.{}'.format(
		module_path[8:],
		cls_name
	)[:100]