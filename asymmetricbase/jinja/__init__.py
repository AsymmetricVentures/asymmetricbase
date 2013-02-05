import datetime
import os, warnings
import locale

from operator import attrgetter

from django.template.loaders.app_directories import fs_encoding, \
	app_template_dirs
from django.core.urlresolvers import reverse
from django.template.defaultfilters import floatformat, yesno, date as date_filter, urlencode
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone
from django.conf import settings

import jinja2
from jinja2.ext import WithExtension, LoopControlExtension
from jinja2.utils import contextfunction

from asymmetricbase.jinja.tags.csrf_token import CSRFTokenExtension
from asymmetricbase.jinja.tags.vtable import VTableExtension
from asymmetricbase.jinja.tags.haml import HamlishTagExtension
from asymmetricbase.jinja.tags.fielditerator import checkboxiterator, checkboxiterator_named, radioiterator, radioiterator_named


class UndefinedVar(jinja2.Undefined):
	def __int__(self):
		return 0
	
	def __float__(self):
		return 0.0
	
	def __str__(self):
		return self.__html__()
	
	def __iter__(self):
		class EmptyIter(object):
			def __iter__(self):
				return self
			def next(self): # @ReservedAssignment
				raise StopIteration()
			
		return EmptyIter()
		
	def __html__(self):
		return u'%NONE%'
	
	def __getattribute__(self, name, *args, **kwargs):
			
		try:
			return super(UndefinedVar, self).__getattribute__(name, *args, **kwargs)
		except AttributeError:
			if settings.TEMPLATE_DEBUG:
				import inspect
				f = inspect.currentframe().f_back.f_back.f_code
				file_name = f.co_filename
				lineno = f.co_firstlineno
				warnings.warn("[{}:{}] Trying to access attribute '{}' on undefined variable '{}'".format(file_name, lineno, name, self._undefined_name))
			return UndefinedVar()
		
		return None

template_loader = getattr(settings, 'ASYM_TEMPLATE_LOADER', jinja2.FileSystemLoader(app_template_dirs))
jinja_env = jinja2.Environment(
	loader = template_loader,
	undefined = UndefinedVar,
	autoescape = True,
	extensions = [
		CSRFTokenExtension,
		VTableExtension,
		HamlishTagExtension,
		WithExtension,
		LoopControlExtension
	]
)

def jinja_url(view_name, *args, **kwargs):
	return reverse(view_name, args = args, kwargs = kwargs)

def jinja_getdate():
	return timezone.localtime(timezone.now())

def jinja_date_filter(d, fmt = "%d/%b/%y %I:%M%p"):
	if not d:
		return ''
	return timezone.localtime(d).strftime(fmt)

def jinja_fmt(fmt, *args, **kwargs):
	return fmt.format(*args, **kwargs)

def jinja_getattr(obj, attr_string):
	"""
	Resolve attributes using jinja's getattr() rather than the default python method.
	
	Will also resolve chained attributes, for example:
	
		getattr(obj, 'user.name')
		
	will resolve obj.user.name
	"""
	if attr_string == '':
		return obj
	attrs = attr_string.split(".")
	for attr in attrs:
		obj = jinja_env.getattr(obj, attr)
	return obj

@contextfunction
def jinja_context_getattr(context, attr_string):
	"""
	Tries to get attribute by name from context
	"""
	return jinja_getattr(context, attr_string)

@contextfunction
def jinja_batch_context_getattr(context, *args, **kwargs):
	new_args = []
	new_kwargs = {}
	if args:
		for arg in args:
			new_args.append(jinja_context_getattr(context, arg))
		return new_args
	if kwargs:
		for k, v in kwargs.items():
			new_kwargs[k] = jinja_context_getattr(context, v)
		return new_kwargs

def jinja_vtable(table, header = '', tail = ''):
	return jinja_env.get_template('asymmetricbase/displaymanager/base.djhtml').module.vtable(table, header, tail)

def jinja_gridlayout(layout):
	return jinja_env.get_template('asymmetricbase/displaymanager/base.djhtml').module.gridlayout(layout)

def jinja_display(layout):
	return jinja_env.get_template('asymmetricbase/displaymanager/base.djhtml').module.display(layout)

def currency_format(num):
	return locale.currency(num, grouping = True)

jinja_env.globals.update({
	'url' : jinja_url,
	'getdatetime' : jinja_getdate,
	'type' : type,
	'dir' : dir,
	'getattr' : jinja_getattr,
	'context_getattr' : jinja_context_getattr,
	'batch_context_getattr' : jinja_batch_context_getattr,
	
	
	'vtable' : jinja_vtable,
	'gridlayout' : jinja_gridlayout,
	'display' : jinja_display,
})

jinja_env.filters.update({
	'date' : jinja_date_filter,
	'floatformat' : floatformat,
	'yesno' : yesno,
	'urlencode' : urlencode,
	'fmt' : jinja_fmt,
	'checkboxiterator' : checkboxiterator,
	'checkboxiterator_named' : checkboxiterator_named,
	'radioiterator' : radioiterator,
	'radioiterator_named' : radioiterator_named,
	'currency' : currency_format,
})
