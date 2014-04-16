import os
import imp
import sys

import six

from django.conf import settings

from jinja2.exceptions import TemplateNotFound
from jinja2.loaders import split_template_path, BaseLoader
from jinja2.utils import open_if_exists, internalcode

try:
	from hamlpy import hamlpy
	from hamlpy import nodes as hamlpynodes
	
	hamlpy.VALID_EXTENSIONS.append('djhaml')
	
	# add jinja tags
	hamlpynodes.TagNode.self_closing.update({
		'macro' : 'endmacro',
		'call' : 'endcall',
	})
	# update for django->jinja
	hamlpynodes.TagNode.may_contain.update({
		'for' : 'else',
	})
except ImportError:
	# hamlpy doesn't work in python3
	hamlpy = None

class ThemeLoader(BaseLoader):
	is_usable = True
	
	def __init__(self, search_paths = None, *args, **kwargs):
		if search_paths is None:
			from django.template.loaders.app_directories import app_template_dirs
			search_paths = app_template_dirs
		
		if isinstance(search_paths, six.string_types):
			search_paths = [search_paths]
		self.search_paths = search_paths
		super(ThemeLoader, self).__init__()
	
	def _get_filenames(self, pieces):
		if not pieces[0].startswith('+'):
			filename_root, ext = os.path.splitext(pieces[-1])
			
			theme = getattr(settings, 'THEME_NAME', None)
			
			if theme is not None:
				new_pieces = pieces[:-1] + ['{}.{}{}'.format(filename_root, theme, ext)]
				yield new_pieces
		else:
			# we want the actual file, not a themed one
			
			pieces = [pieces[0][1:]] + list(pieces[1:])
		
		yield pieces
	
	@internalcode
	def load(self, environment, name, global_vars = None):
		if getattr(settings, 'COMPILE_TEMPLATES', False):
			if settings.TEMPLATE_DEBUG:
				sys.dont_write_bytecode = True
			code = None
			if global_vars is None:
				global_vars = {}
			# Check if we have a precompiled version
			if not self._is_compiled(name):
				# if not, compile
				source, filename, _ = self.get_source(environment, name)
				code = environment.compile(source, name, filename, raw = True, defer_init = True)
				
				# and then save
				fp = open(self._get_compiled_path(name), 'w')
				try:
					fp.write(code)
				finally:
					fp.close()
			
			compiled_path = self._get_compiled_path(name)
			module_name = os.path.splitext(name)[0].replace('/', '_')
			module = imp.load_source(module_name, compiled_path)
			
			return environment.template_class.from_module_dict(environment, module.__dict__, global_vars)
		else:
			return super(ThemeLoader, self).load(environment, name, global_vars)
	
	def _is_compiled(self, path):
		compiled_path = self._get_compiled_path(path)
		full_path, _ = self.get_full_template_path(path)
		
		if not os.path.exists(compiled_path):
			return False
		
		# If the source has been updated, recompile
		return os.path.getmtime(full_path) < os.path.getmtime(compiled_path)
	
	def _get_compiled_path(self, template_path):
		
		full_template_path, _ = self.get_full_template_path(template_path)
		
		if not full_template_path.endswith('.djhtml'):
			raise TemplateNotFound(full_template_path, "File does not end with correct extension")
		
		return full_template_path.replace('.djhtml', '_compiled.py')
	
	def get_source(self, environment, template):
		
		filename, ext = self.get_full_template_path(template)
		fp = open_if_exists(filename)
		if fp is None:
			raise TemplateNotFound(template)
		try:
			#print("Loading: {}".format(filename))
			contents = fp.read().decode('utf-8')
			
			if hamlpy and ext[1:] in hamlpy.VALID_EXTENSIONS:
				haml_parser = hamlpy.Compiler()
				contents = haml_parser.process(contents)
		except UnicodeDecodeError:
			raise TemplateNotFound(template)
		
		finally:
			fp.close()
		
		mtime = os.path.getmtime(filename)
		def uptodate():
			try:
				return os.path.getmtime(filename) == mtime
			except OSError:
				return False
		return contents, filename, uptodate
	
	def get_full_template_path(self, template):
		
		for path in self.search_paths:
			for pieces in self._get_filenames(split_template_path(template)):
				filename = os.path.join(path, *pieces)
				
				if os.path.exists(filename):
					ext = os.path.splitext(pieces[-1])[-1]
					return filename, ext
		
		raise TemplateNotFound(template)
	
	def list_templates(self):
		found = set()
		
		for path in self.search_paths:
			for dirpath, _, filenames in os.walk(path):
				for filename in filenames:
					template_path = os.path.join(dirpath, filename)
					template = template_path[len(path):].strip(os.path.sep).replace(os.path.sep, '/')
					
					template_ext = os.path.splitext(template)[-1]
					
					if template_ext in getattr(settings, 'INVALID_TEMPLATE_EXTS', ('.py', '.pyc')):
						continue
					
					if template[:2] == './':
						template = template[2:]
					if template not in found:
						found.add(template)
		
		return sorted(found)
