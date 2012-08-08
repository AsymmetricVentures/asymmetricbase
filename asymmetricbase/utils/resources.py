import os
import re

from django.conf import settings
from django.utils.safestring import mark_safe

static_dir = settings.STATIC_DOC_ROOT

class ResourceType(object):
	def __init__(self, folder, extension, html):
		self.folder = folder
		self.extension = extension
		self.html = html
	
	def __repr__(self):
		return self.extension

ResourceType.JS = ResourceType(
	folder = 'js', extension = 'js',
	html = u'<script src="{url}?h={hash}" type="text/javascript"></script>',
)

ResourceType.CSS = ResourceType(
	folder = 'stylesheets', extension = 'css',
	html = u'<link href="{url}?h={hash}" rel="stylesheet" type="text/css"/>',
)

class Resource(object):
	def __init__(self, resource_type, file_path, dependencies):
		self.file = file_path
		self.hash = _calc_file_hash(os.path.join(static_dir, file_path))
		self.type = resource_type
		self.dependencies = dependencies
		self.url = '{}{}'.format(
			settings.MEDIA_URL, self.file
		)
	
	def __html__(self):
		return mark_safe(self.type.html.format(url = self.url, hash = self.hash))
	
	def __str__(self):
		return self.__html__()
	
	def __unicode__(self):
		return str(self)
	
	def __hash__(self):
		return hash(self.file)
	
	def __repr__(self):
		return u"Resource('{}')".format(self.file)

class ResourceSet(object):
	def __init__(self):
		self._all = get_resources()
		self._included = []
	
	def add(self, resources):
		for resource in resources:
			resource = _normalize_resource_filename(resource)
			if resource not in self._all:
				raise MissingResourceException(resource)
			self._included.append(self._all[resource])
	
	def __html__(self):
		
		closure = set()
		closure_list = []
		for resource in self._included:
			self._resource_closure(closure, closure_list, resource)
		
		return mark_safe('\n'.join(resource.__html__() for resource in closure_list))
	
	def as_html(self):
		return self.__html__()
	
	def _resource_closure(self, out, out_list, resource):
		if resource in out:
			return
		for dep in resource.dependencies:
			self._resource_closure(out, out_list, self._all[dep])
		out.add(resource)
		out_list.append(resource)

_resources_cache = None

def get_resources():
	global _resources_cache
	if _resources_cache is None:
		_resources_cache = _get_resources()
	return _resources_cache

def _get_resources():
	
	resources = {}
	
	resource_types = [
		ResourceType.JS, ResourceType.CSS
	]
	
	for resource_type in resource_types:
		rootdir = os.path.join(static_dir, resource_type.folder)
		for file_path in _list_files_of_type(rootdir, resource_type.extension):
			deps = _get_file_dependencies(file_path)
			relfile = _normalize_resource_filename(file_path)
			resources[relfile] = Resource(resource_type, relfile, deps)
	
	_validate_dependencies(resources)
	
	return resources

def _normalize_resource_filename(file_path):
	if file_path.startswith(static_dir):
		relfile = os.path.relpath(file_path, static_dir)
	else:
		relfile = file_path
	return relfile.replace('\\', '/')

def _validate_dependencies(resources):
	dependency_problems = []
	
	for resource in resources.values():
		for dep in resource.dependencies:
			if dep not in resources:
				dependency_problems.append((resource, dep))
	
	if dependency_problems:
		raise MissingResourceDependencyException(dependency_problems)

class ResourceException(Exception):
	pass

class MissingResourceDependencyException(ResourceException):
	def __init__(self, dependency_problems):
		self.dependency_problems = dependency_problems
	
	def __str__(self):
		return 'Several resource dependencies cannot be satisfied:\n{}'.format(
			repr(self.dependency_problems)
		)

class MissingResourceException(ResourceException):
	def __init__(self, resource):
		self.resource = resource
	
	def __str__(self):
		return 'Missing resource: {}'.format(self.resource)

def _list_files_of_type(rootdir, ext):
	dotext = '.' + ext
	
	for r, _, files in os.walk(rootdir):
		for file_name in files:
			if file_name.endswith(dotext):
				yield os.path.join(r, file_name)

def _get_file_dependencies(file_path):
	deps = []
	
	for line in open(file_path, 'rb'):
		m = re.search(r'#require\s+(\S+)', line)
		if m:
			deps.append(m.group(1))
	
	return deps

def _calc_file_hash(filename):
	return _md5_for_file(filename)[0:6]

def _md5_for_file(filename):
	import hashlib
	
	block_size = 131072
	
	md5 = hashlib.md5()
	
	f = open(filename, 'rb')
	while True:
		data = f.read(block_size)
		if not data:
			break
		md5.update(data)
	
	return md5.hexdigest()
