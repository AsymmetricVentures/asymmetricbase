# -*- coding: utf-8 -*-
#    Asymmetric Base Framework - A collection of utilities for django frameworks
#    Copyright (C) 2013  Asymmetric Ventures Inc.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; version 2 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import re

from django.conf import settings
from django.utils.safestring import mark_safe

static_dir = settings.STATIC_ROOT

class ResourceType(object):
	resource_types = {}
	
	def __init__(self, folder, extension, html):
		self.folder = folder
		self.extension = extension
		self.html = html
	
	def __repr__(self):
		return self.extension
	
	@classmethod
	def add_resource_type(cls, name, folder, extension, html):
		cls.resource_types[name] = ResourceType(folder = folder, extension = extension, html = html)

class Resource(object):
	def __init__(self, resource_type, file_path, dependencies):
		self.file = file_path
		self.hash = _calc_file_hash(os.path.join(static_dir, file_path))
		self.type = resource_type
		self.dependencies = dependencies
		self.url = '{}{}'.format(
			settings.STATIC_URL, self.file
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
		return "Resource('{}')".format(self.file)
	
	@property
	def absolute_path(self):
		"""
		The absolute path of the file.
		"""
		return '{}{}'.format(settings.STATIC_ROOT, self.file)

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
		closure_list = self._get_resource_closure_list()
		return mark_safe('\n'.join(resource.__html__() for resource in closure_list))
	
	def as_html(self):
		return self.__html__()
	
	def as_absolute_path_list(self):
		"""
		Return a list of files in the set as absolute paths.
		"""
		closure_list = self._get_resource_closure_list()
		return [resource.absolute_path for resource in closure_list]
	
	def _get_resource_closure_list(self):
		"""
		Return a list of all files in the set and their dependencies.
		"""
		closure = set()
		closure_list = []
		for resource in self._included:
			self._resource_closure(closure, closure_list, resource)
		return closure_list
	
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
	
	for resource_type in ResourceType.resource_types.values():
		rootdir = os.path.join(static_dir, resource_type.folder)
		for file_path in _list_files_of_type(rootdir, resource_type.extension):
			deps = _get_file_dependencies(file_path)
			relfile = _normalize_resource_filename(file_path)
			resources[_normalize_resource_filename(relfile, resource_type.folder)] = Resource(resource_type, relfile, deps)
	
	_validate_dependencies(resources)
	
	return resources

def _normalize_resource_filename(file_path, normalize_base = static_dir):
	if file_path.startswith(normalize_base):
		relfile = os.path.relpath(file_path, normalize_base)
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
	
	for r, dirs, files in os.walk(rootdir):
		for d in dirs:
			for f in _list_files_of_type(os.path.join(rootdir, d), ext):
				yield f
		for file_name in files:
			if file_name.endswith(dotext):
				yield os.path.join(r, file_name)

def _get_file_dependencies(file_path):
	deps = []
	
	for line in open(file_path, 'rb'):
		m = re.search(r'^\s*\/\/\s*import\s+(\S+);', line)
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
