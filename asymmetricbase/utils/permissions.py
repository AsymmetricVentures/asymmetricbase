from django.contrib.contenttypes.models import ContentType

def default_content_type():
	return ContentType.objects.get(model = 'user')

def create_codename(module_path, cls_name):
	return 'view_permission_{}.{}'.format(module_path, cls_name)